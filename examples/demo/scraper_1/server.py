
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

DATABASE = 'crm.db'
ENTRIES_PER_PAGE = 10

# Virtual Agent Configuration
AGENT_NAME = "Web Search & Scraper Agent"
AGENT_AVATAR = "https://robohash.org/WebSearchScraperAgent.png?size=100x100&set=set3"
AGENT_PROMPT = '''Advanced competitor searcher and web scraper.

Search internet to find all information of competitor company "wordware.ai". 
Then scrape the found URLs for more detailed information.
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
        conn.execute('''CREATE TABLE IF NOT EXISTS crm_entries
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         title TEXT,
                         link TEXT,
                         content TEXT,
                         webpage_content TEXT,
                         scrape_status TEXT,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()


def produce_data_point(data_entry: dict):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            title = data_entry.get('title', '')
            link = data_entry.get('link', '')
            content = data_entry.get('content', '')
            webpage_content = ''
            scrape_status = 'pending'

            c.execute("INSERT INTO crm_entries (title, link, content, webpage_content, scrape_status) VALUES (?, ?, ?, ?, ?)",
                      (title, link, content, webpage_content, scrape_status))
            conn.commit()

            new_entry = c.execute("SELECT * FROM crm_entries WHERE id = last_insert_rowid()").fetchone()

        socketio.emit('new_entry', dict(new_entry))
        print(f"New entry added and emitted: {dict(new_entry)}")

        # Start scraping the URL in a separate thread
        threading.Thread(target=scrape_url, args=(link,)).start()

    except Exception as e:
        print(f"Error in produce_data_point: {str(e)}")
        traceback.print_exc()


def ingest_data():
    global data_generation_active
    while data_generation_active:
        web_search_agent(AGENT_PROMPT, produce_data_point)
        time.sleep(10)


def scrape_url(url):
    def scrape_producer(data):
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute("UPDATE crm_entries SET webpage_content = ?, scrape_status = ? WHERE link = ?",
                          (data['webpage_content'], 'scraped', data['url']))
                conn.commit()
            
            socketio.emit('entry_updated', {'url': url, 'webpage_content': data['webpage_content'], 'scrape_status': 'scraped'})
        except Exception as e:
            print(f"Error in scrape_producer: {str(e)}")
            update_scrape_status(url, 'failed')

    try:
        web_scraper_agent(url, scrape_producer)
    except Exception as e:
        print(f"Error in scrape_url: {str(e)}")
        update_scrape_status(url, 'failed')


def update_scrape_status(url, status):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE crm_entries SET scrape_status = ? WHERE link = ?", (status, url))
            conn.commit()
        
        socketio.emit('entry_updated', {'url': url, 'scrape_status': status})
    except Exception as e:
        print(f"Error in update_scrape_status: {str(e)}")


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/entries', methods=['GET'])
def get_entries():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ENTRIES_PER_PAGE

    with get_db_connection() as conn:
        total_entries = conn.execute("SELECT COUNT(*) FROM crm_entries").fetchone()[0]
        entries = conn.execute("SELECT * FROM crm_entries ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                               (ENTRIES_PER_PAGE, offset)).fetchall()

    return jsonify({
        'entries': [dict(entry) for entry in entries],
        'total_entries': total_entries,
        'total_pages': (total_entries + ENTRIES_PER_PAGE - 1) // ENTRIES_PER_PAGE
    })


@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.json
    if not data or 'title' not in data or 'link' not in data or 'content' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO crm_entries (title, link, content, scrape_status) VALUES (?, ?, ?, ?)",
                  (data['title'], data['link'], data['content'], 'pending'))
        conn.commit()
        new_id = c.lastrowid

        new_entry = c.execute("SELECT * FROM crm_entries WHERE id = ?", (new_id,)).fetchone()

    socketio.emit('new_entry', dict(new_entry))

    # Start scraping the URL in a separate thread
    threading.Thread(target=scrape_url, args=(data['link'],)).start()

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
        cursor.execute("SELECT * FROM crm_entries ORDER BY timestamp DESC")
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['id', 'title', 'link', 'content', 'webpage_content', 'scrape_status', 'timestamp'])
    
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='crm_entries.csv'
    )


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    init_db()
    port = 8593
    print(f"Server running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
