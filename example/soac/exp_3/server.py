import sqlite3
import threading
import time
from functools import partial

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from finae import web_search_agent

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = 'crm.db'
ENTRIES_PER_PAGE = 10

# Virtual Agent Configuration
AGENT_NAME = "DataBot"
AGENT_AVATAR = "https://robohash.org/DataBot.png?size=100x100&set=set3"
AGENT_PROMPT = '''Advanced competitor searcher.

Search internet to find all information of competitor comapny "wordware.ai". 
'''

# Data generation control
data_generation_active = False
data_generation_thread = None


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS crm_entries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  link TEXT,
                  content TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


def produce_data_point(conn, c, data_entry: dict):
    try:
        # Generate sample data
        title = data_entry['title']
        link = data_entry['link']
        content = data_entry['content']

        c.execute("INSERT INTO crm_entries (title, link, content) VALUES (?, ?, ?)",
                  (title, link, content))
        conn.commit()

        # Fetch the newly inserted entry
        c.execute("SELECT * FROM crm_entries WHERE id = last_insert_rowid()")
        new_entry = c.fetchone()
        conn.close()

        # Emit the new entry to all connected clients
        socketio.emit('new_entry', {
            'id': new_entry[0],
            'title': new_entry[1],
            'link': new_entry[2],
            'content': new_entry[3],
            'timestamp': new_entry[4]
        })
    except:
        pass


def ingest_data():
    global data_generation_active
    while data_generation_active:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        web_search_agent(AGENT_PROMPT, partial(produce_data_point, conn, c))
        time.sleep(5)  # Simulate delay between data points


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/entries', methods=['GET'])
def get_entries():
    page = request.args.get('page', 1, type=int)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Get total count of entries
    c.execute("SELECT COUNT(*) FROM crm_entries")
    total_entries = c.fetchone()[0]

    # Calculate offset
    offset = (page - 1) * ENTRIES_PER_PAGE

    # Fetch paginated entries
    c.execute("SELECT * FROM crm_entries ORDER BY timestamp DESC LIMIT ? OFFSET ?",
              (ENTRIES_PER_PAGE, offset))
    entries = c.fetchall()
    conn.close()

    return jsonify({
        'entries': [{
            'id': entry[0],
            'title': entry[1],
            'link': entry[2],
            'content': entry[3],
            'timestamp': entry[4]
        } for entry in entries],
        'total_entries': total_entries,
        'total_pages': (total_entries + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })


@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.json
    if not data or 'title' not in data or 'link' not in data or 'content' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO crm_entries (title, link, content) VALUES (?, ?, ?)",
              (data['title'], data['link'], data['content']))
    conn.commit()
    new_id = c.lastrowid

    # Fetch the newly inserted entry
    c.execute("SELECT * FROM crm_entries WHERE id = ?", (new_id,))
    new_entry = c.fetchone()
    conn.close()

    # Emit the new entry to all connected clients
    socketio.emit('new_entry', {
        'id': new_entry[0],
        'title': new_entry[1],
        'link': new_entry[2],
        'content': new_entry[3],
        'timestamp': new_entry[4]
    })

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


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    init_db()
    port = 8889
    print(f"Server running on port {port}")
    socketio.run(app, host='localhost', port=port, debug=True)
