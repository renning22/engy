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
from engy import airbnb_review_agent, query_llm

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = 'airbnb_cx.db'
ENTRIES_PER_PAGE = 10

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

        conn.execute('''CREATE TABLE IF NOT EXISTS cx_insights
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         summary TEXT,
                         count INTEGER DEFAULT 1,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        conn.execute('''CREATE TABLE IF NOT EXISTS cx_actions
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         action TEXT,
                         insight_id INTEGER,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                         FOREIGN KEY (insight_id) REFERENCES cx_insights (id))''')

        conn.execute('''CREATE TABLE IF NOT EXISTS product_decisions
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         decision TEXT,
                         insight_id INTEGER,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                         FOREIGN KEY (insight_id) REFERENCES cx_insights (id))''')
        conn.commit()

def generate_random_review():
    review_data = None

    def review_producer(review):
        nonlocal review_data
        review_data = review

    airbnb_review_agent(review_producer)
    return review_data

INSIGHT_SYSTEM_PROMPT = '''You are an expert CX (Customer Experience) analyst for Airbnb. Your task is to analyze customer reviews and extract valuable insights to improve the product and increase ROI (Return on Investment).

For each review, you should:
1. Identify the main issue or concern raised by the customer.
2. Summarize the issue in a very short, 2-word phrase.
3. Suggest an actionable step to address the issue and improve the customer experience.
4. Propose a product decision based on the insight.

Your output should be in the following format:
<INSIGHT>
Summary: [2-word phrase summarizing the issue]
Action: [Suggested action to address the issue]
Decision: [Proposed product decision]
</INSIGHT>'''

def analyze_review_and_generate_insight(review):
    query = f"Analyze the following Airbnb review and extract an insight:\n\n{review['review_content']}"
    
    responses, _ = query_llm(query, system_message=INSIGHT_SYSTEM_PROMPT,
                             model="claude-3-5-sonnet-20240620", temperature=0.2, filename='cx_insight_agent')
    
    insight_text = responses[0]
    start_tag = "<INSIGHT>"
    end_tag = "</INSIGHT>"
    
    if start_tag in insight_text and end_tag in insight_text:
        insight_content = insight_text[insight_text.find(start_tag) + len(start_tag):insight_text.find(end_tag)].strip()
        summary = insight_content.split("Summary:")[1].split("Action:")[0].strip()
        action = insight_content.split("Action:")[1].split("Decision:")[0].strip()
        decision = insight_content.split("Decision:")[1].strip()
        return {"summary": summary, "action": action, "decision": decision}
    
    return None

def store_or_update_insight(insight):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM cx_insights WHERE summary = ?", (insight['summary'],))
        existing_insight = c.fetchone()
        
        if existing_insight:
            c.execute("UPDATE cx_insights SET count = count + 1 WHERE id = ?", (existing_insight['id'],))
            insight_id = existing_insight['id']
        else:
            c.execute("INSERT INTO cx_insights (summary) VALUES (?)", (insight['summary'],))
            insight_id = c.lastrowid
        conn.commit()

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO cx_actions (action, insight_id) VALUES (?, ?)", (insight['action'], insight_id))
        conn.commit()

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO product_decisions (decision, insight_id) VALUES (?, ?)", (insight['decision'], insight_id))
        conn.commit()

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

    insight = analyze_review_and_generate_insight(dict(new_review))
    if insight:
        store_or_update_insight(insight)

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

    insight = analyze_review_and_generate_insight(dict(new_review))
    if insight:
        store_or_update_insight(insight)

    socketio.emit('new_review', dict(new_review))

    return jsonify({'id': new_id, 'message': 'Random review generated and added successfully'}), 201

@app.route('/api/insights', methods=['GET'])
def get_insights():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ENTRIES_PER_PAGE

    with get_db_connection() as conn:
        total_insights = conn.execute("SELECT COUNT(*) FROM cx_insights").fetchone()[0]
        insights = conn.execute("SELECT * FROM cx_insights ORDER BY count DESC, timestamp DESC LIMIT ? OFFSET ?",
                                (ENTRIES_PER_PAGE, offset)).fetchall()

    return jsonify({
        'insights': [dict(insight) for insight in insights],
        'total_insights': total_insights,
        'total_pages': (total_insights + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })

@app.route('/api/actions', methods=['GET'])
def get_actions():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ENTRIES_PER_PAGE

    with get_db_connection() as conn:
        total_actions = conn.execute("SELECT COUNT(*) FROM cx_actions").fetchone()[0]
        actions = conn.execute("""
            SELECT ca.*, ci.summary
            FROM cx_actions ca
            JOIN cx_insights ci ON ca.insight_id = ci.id
            ORDER BY ca.timestamp DESC
            LIMIT ? OFFSET ?
        """, (ENTRIES_PER_PAGE, offset)).fetchall()

    return jsonify({
        'actions': [dict(action) for action in actions],
        'total_actions': total_actions,
        'total_pages': (total_actions + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })

@app.route('/api/decisions', methods=['GET'])
def get_decisions():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ENTRIES_PER_PAGE

    with get_db_connection() as conn:
        total_decisions = conn.execute("SELECT COUNT(*) FROM product_decisions").fetchone()[0]
        decisions = conn.execute("""
            SELECT pd.*, ci.summary
            FROM product_decisions pd
            JOIN cx_insights ci ON pd.insight_id = ci.id
            ORDER BY pd.timestamp DESC
            LIMIT ? OFFSET ?
        """, (ENTRIES_PER_PAGE, offset)).fetchall()

    return jsonify({
        'decisions': [dict(decision) for decision in decisions],
        'total_decisions': total_decisions,
        'total_pages': (total_decisions + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })

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
    port = 6442
    print(f"Server running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)