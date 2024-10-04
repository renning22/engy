
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Database setup
conn = sqlite3.connect('dashboard.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY,
    name TEXT,
    role TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ticket (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    agent_id INTEGER,
    status TEXT,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS response (
    id INTEGER PRIMARY KEY,
    ticket_id INTEGER,
    agent_id INTEGER,
    timestamp TIMESTAMP
)
''')

conn.commit()

# Data generation function
def generate_random_data():
    # Generate persons
    roles = ['customer', 'agent']
    for i in range(50):
        name = f"Person {i+1}"
        role = random.choice(roles)
        cursor.execute("INSERT INTO person (name, role) VALUES (?, ?)", (name, role))

    # Generate tickets and responses
    for i in range(100):
        customer_id = random.randint(1, 50)
        agent_id = random.randint(1, 50)
        status = random.choice(['open', 'closed'])
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        resolved_at = created_at + timedelta(hours=random.randint(1, 48)) if status == 'closed' else None
        
        cursor.execute("INSERT INTO ticket (customer_id, agent_id, status, created_at, resolved_at) VALUES (?, ?, ?, ?, ?)",
                       (customer_id, agent_id, status, created_at, resolved_at))
        
        ticket_id = cursor.lastrowid
        
        # Generate responses for this ticket
        for _ in range(random.randint(1, 5)):
            response_timestamp = created_at + timedelta(minutes=random.randint(30, 120))
            cursor.execute("INSERT INTO response (ticket_id, agent_id, timestamp) VALUES (?, ?, ?)",
                           (ticket_id, agent_id, response_timestamp))

    conn.commit()

# Dashboard data calculation functions
def calculate_ticket_volume():
    cursor.execute("SELECT COUNT(*) FROM ticket")
    return cursor.fetchone()[0]

def calculate_avg_response_time():
    cursor.execute("""
    SELECT AVG(JULIANDAY(r.timestamp) - JULIANDAY(t.created_at)) * 24 * 60
    FROM ticket t
    JOIN response r ON t.id = r.ticket_id
    WHERE r.timestamp = (SELECT MIN(timestamp) FROM response WHERE ticket_id = t.id)
    """)
    return cursor.fetchone()[0]

def calculate_avg_resolution_time():
    cursor.execute("""
    SELECT AVG(JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24
    FROM ticket
    WHERE status = 'closed'
    """)
    return cursor.fetchone()[0]

def calculate_sla_adherence():
    cursor.execute("""
    SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ticket)
    FROM ticket
    WHERE JULIANDAY(resolved_at) - JULIANDAY(created_at) <= 2
    """)
    return cursor.fetchone()[0]

# API endpoints
@app.route('/api/dashboard')
def get_dashboard_data():
    return jsonify({
        'ticket_volume': calculate_ticket_volume(),
        'avg_response_time': calculate_avg_response_time(),
        'avg_resolution_time': calculate_avg_resolution_time(),
        'sla_adherence': calculate_sla_adherence()
    })

@app.route('/api/tickets')
def get_ticket_data():
    cursor.execute("""
    SELECT t.id, p1.name as customer, p2.name as agent, t.status, t.created_at, t.resolved_at
    FROM ticket t
    JOIN person p1 ON t.customer_id = p1.id
    JOIN person p2 ON t.agent_id = p2.id
    """)
    tickets = [{'id': row[0], 'customer': row[1], 'agent': row[2], 'status': row[3], 'created_at': row[4], 'resolved_at': row[5]}
               for row in cursor.fetchall()]
    return jsonify(tickets)

@app.route('/api/agents')
def get_agent_data():
    cursor.execute("""
    SELECT p.name, COUNT(t.id) as tickets_handled, AVG(JULIANDAY(t.resolved_at) - JULIANDAY(t.created_at)) * 24 as avg_resolution_time
    FROM person p
    JOIN ticket t ON p.id = t.agent_id
    WHERE p.role = 'agent'
    GROUP BY p.id
    """)
    agents = [{'name': row[0], 'tickets_handled': row[1], 'avg_resolution_time': row[2]}
              for row in cursor.fetchall()]
    return jsonify(agents)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    if not os.path.exists('dashboard.db'):
        generate_random_data()
    app.run(host='localhost', port=5123, debug=True)
