
import sqlite3
import threading
import time
import traceback
import csv
import io

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_socketio import SocketIO

from engy import web_search_agent, web_scraper_agent

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = 'ux_insights.db'
ENTRIES_PER_PAGE = 10

# Virtual Agent Configuration
AGENT_NAME = "UX Insights Agent"
AGENT_AVATAR = "https://robohash.org/UXInsightsAgent.png?size=100x100&set=set3"
AGENT_PROMPT = '''Advanced UX insights and user feedback analyzer.

Search the internet to find user product feedback and UX insights for various products.
Then analyze the found information for detailed UX insights.
'''

# Data generation control
data_generation_active = False
data_generation_thread = None


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS ux_insights
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         product_name TEXT,
                         user_feedback TEXT,
                         ux_insight TEXT,
                         sentiment TEXT,
                         source_url TEXT,
                         analysis_status TEXT,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()


def produce_data_point(data_entry: dict):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            product_name = data_entry.get('product_name', '')
            user_feedback = data_entry.get('user_feedback', '')
            source_url = data_entry.get('source_url', '')
            ux_insight = ''
            sentiment = ''
            analysis_status = 'pending'

            c.execute("INSERT INTO ux_insights (product_name, user_feedback, ux_insight, sentiment, source_url, analysis_status) VALUES (?, ?, ?, ?, ?, ?)",
                      (product_name, user_feedback, ux_insight, sentiment, source_url, analysis_status))
            conn.commit()

            new_entry = c.execute("SELECT * FROM ux_insights WHERE id = last_insert_rowid()").fetchone()

        socketio.emit('new_entry', dict(new_entry))
        print(f"New entry added and emitted: {dict(new_entry)}")

        # Start analyzing the feedback in a separate thread
        threading.Thread(target=analyze_feedback, args=(new_entry['id'],)).start()

    except Exception as e:
        print(f"Error in produce_data_point: {str(e)}")
        traceback.print_exc()


def ingest_data():
    global data_generation_active
    while data_generation_active:
        web_search_agent(AGENT_PROMPT, produce_data_point)
        time.sleep(10)


def analyze_feedback(entry_id):
    def analysis_producer(data):
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute("UPDATE ux_insights SET ux_insight = ?, sentiment = ?, analysis_status = ? WHERE id = ?",
                          (data['ux_insight'], data['sentiment'], 'analyzed', entry_id))
                conn.commit()
            
            socketio.emit('entry_updated', {'id': entry_id, 'ux_insight': data['ux_insight'], 'sentiment': data['sentiment'], 'analysis_status': 'analyzed'})
        except Exception as e:
            print(f"Error in analysis_producer: {str(e)}")
            update_analysis_status(entry_id, 'failed')

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            entry = c.execute("SELECT * FROM ux_insights WHERE id = ?", (entry_id,)).fetchone()
        
        # Here you would typically call an AI model to analyze the feedback
        # For this example, we'll use a placeholder function
        analyze_ux_feedback(entry['user_feedback'], analysis_producer)
    except Exception as e:
        print(f"Error in analyze_feedback: {str(e)}")
        update_analysis_status(entry_id, 'failed')


def analyze_ux_feedback(feedback, producer):
    # This is a placeholder function. In a real scenario, you'd use an AI model here.
    ux_insight = f"Analysis of: {feedback[:50]}..."
    sentiment = "positive" if "good" in feedback.lower() else "negative"
    producer({'ux_insight': ux_insight, 'sentiment': sentiment})


def update_analysis_status(entry_id, status):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE ux_insights SET analysis_status = ? WHERE id = ?", (status, entry_id))
            conn.commit()
        
        socketio.emit('entry_updated', {'id': entry_id, 'analysis_status': status})
    except Exception as e:
        print(f"Error in update_analysis_status: {str(e)}")


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/entries', methods=['GET'])
def get_entries():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ENTRIES_PER_PAGE

    with get_db_connection() as conn:
        total_entries = conn.execute("SELECT COUNT(*) FROM ux_insights").fetchone()[0]
        entries = conn.execute("SELECT * FROM ux_insights ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                               (ENTRIES_PER_PAGE, offset)).fetchall()

    return jsonify({
        'entries': [dict(entry) for entry in entries],
        'total_entries': total_entries,
        'total_pages': (total_entries + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })


@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.json
    if not data or 'product_name' not in data or 'user_feedback' not in data or 'source_url' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO ux_insights (product_name, user_feedback, source_url, analysis_status) VALUES (?, ?, ?, ?)",
                  (data['product_name'], data['user_feedback'], data['source_url'], 'pending'))
        conn.commit()
        new_id = c.lastrowid

        new_entry = c.execute("SELECT * FROM ux_insights WHERE id = ?", (new_id,)).fetchone()

    socketio.emit('new_entry', dict(new_entry))

    # Start analyzing the feedback in a separate thread
    threading.Thread(target=analyze_feedback, args=(new_id,)).start()

    return jsonify({'id': new_id, 'message': 'Entry added successfully'}), 201


@app.route('/api/agent', methods=['GET'])
def get_agent_info():
    return jsonify({
        'name': AGENT_NAME,
        'avatar': AGENT_AVATAR
    })


@app.route('/api/data_generation/start', methods=['POST'])
def start_data_generation():
    global data_generation_active, data_generation_thread
    if not data_generation_active:
        data_generation_active = True
        data_generation_thread = threading.Thread(target=ingest_data)
        data_generation_thread.start()
        return jsonify({'message': 'Data generation started'}), 200
    return jsonify({'message': 'Data generation already running'}), 200


@app.route('/api/data_generation/stop', methods=['POST'])
def stop_data_generation():
    global data_generation_active, data_generation_thread
    if data_generation_active:
        data_generation_active = False
        if data_generation_thread:
            data_generation_thread.join()
        return jsonify({'message': 'Data generation stopped'}), 200
    return jsonify({'message': 'Data generation not running'}), 200


@app.route('/api/data_generation/status', methods=['GET'])
def get_data_generation_status():
    global data_generation_active
    return jsonify({'active': data_generation_active})


@app.route('/api/export_csv', methods=['GET'])
def export_csv():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ux_insights ORDER BY timestamp DESC")
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['id', 'product_name', 'user_feedback', 'ux_insight', 'sentiment', 'source_url', 'analysis_status', 'timestamp'])
    
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='ux_insights.csv'
    )


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    init_db()
    port = 8179
    print(f"Server running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
