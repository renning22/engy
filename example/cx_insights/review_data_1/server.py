
import sqlite3
import threading
import time
import traceback
import csv
import io
from typing import Callable

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_socketio import SocketIO
from finae import airbnb_review_agent

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = 'customer_reviews.db'
ENTRIES_PER_PAGE = 10

# Data generation control
data_generation_active = False
data_generation_thread = None

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS customer_reviews
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT,
                         date TEXT,
                         platform TEXT,
                         review_content TEXT,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()

def generate_random_review():
    review_data = None

    def review_producer(review):
        nonlocal review_data
        review_data = review

    airbnb_review_agent(review_producer)
    return review_data

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ENTRIES_PER_PAGE

    with get_db_connection() as conn:
        total_reviews = conn.execute("SELECT COUNT(*) FROM customer_reviews").fetchone()[0]
        reviews = conn.execute("SELECT * FROM customer_reviews ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                               (ENTRIES_PER_PAGE, offset)).fetchall()

    return jsonify({
        'reviews': [dict(review) for review in reviews],
        'total_reviews': total_reviews,
        'total_pages': (total_reviews + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    if not data or 'name' not in data or 'date' not in data or 'platform' not in data or 'review_content' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO customer_reviews (name, date, platform, review_content) VALUES (?, ?, ?, ?)",
                  (data['name'], data['date'], data['platform'], data['review_content']))
        conn.commit()
        new_id = c.lastrowid

        new_review = c.execute("SELECT * FROM customer_reviews WHERE id = ?", (new_id,)).fetchone()

    socketio.emit('new_review', dict(new_review))

    return jsonify({'id': new_id, 'message': 'Review added successfully'}), 201

@app.route('/api/generate_review', methods=['POST'])
def generate_review():
    review = generate_random_review()
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO customer_reviews (name, date, platform, review_content) VALUES (?, ?, ?, ?)",
                  (review['name'], review['date'], review['platform'], review['review_content']))
        conn.commit()
        new_id = c.lastrowid

        new_review = c.execute("SELECT * FROM customer_reviews WHERE id = ?", (new_id,)).fetchone()

    socketio.emit('new_review', dict(new_review))

    return jsonify({'id': new_id, 'message': 'Random review generated and added successfully'}), 201

@app.route('/api/export_csv', methods=['GET'])
def export_csv():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer_reviews ORDER BY timestamp DESC")
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['id', 'name', 'date', 'platform', 'review_content', 'timestamp'])
    
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='customer_reviews.csv'
    )

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    init_db()
    port = 9722
    print(f"Server running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
