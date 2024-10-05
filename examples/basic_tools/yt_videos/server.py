
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# YouTube API configuration
YOUTUBE_API_KEY = 'AIzaSyBn2-7SCcsZwnLvJVUjf36Mwu5bYW30Uh0'  # Replace with your actual API key
YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/videos'

# Database setup
DB_NAME = 'videos.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  youtube_id TEXT UNIQUE,
                  title TEXT,
                  description TEXT,
                  tags TEXT,
                  added_date DATETIME)''')
    conn.commit()
    conn.close()

init_db()

def fetch_video_info(youtube_id):
    params = {
        'part': 'snippet',
        'id': youtube_id,
        'key': YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_API_URL, params=params)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        snippet = data['items'][0]['snippet']
        return {
            'title': snippet['title'],
            'description': snippet['description']
        }
    return None

def parse_tags(description):
    # Simple tag extraction (you may want to improve this)
    words = description.lower().split()
    tags = [word for word in words if word.startswith('#')]
    return ','.join(tags)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/videos', methods=['GET'])
def get_videos():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM videos")
    videos = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
    conn.close()
    return jsonify(videos)

@app.route('/videos', methods=['POST'])
def add_video():
    youtube_id = request.json.get('youtube_id')
    if not youtube_id:
        return jsonify({"error": "YouTube ID is required"}), 400

    video_info = fetch_video_info(youtube_id)
    if not video_info:
        return jsonify({"error": "Unable to fetch video information"}), 400

    title = video_info['title']
    description = video_info['description']
    tags = parse_tags(description)
    added_date = datetime.now().isoformat()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO videos (youtube_id, title, description, tags, added_date) VALUES (?, ?, ?, ?, ?)",
                  (youtube_id, title, description, tags, added_date))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Video already exists"}), 400
    conn.close()

    return jsonify({"message": "Video added successfully"}), 201

@app.route('/videos/<int:id>', methods=['DELETE'])
def delete_video(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM videos WHERE id = ?", (id,))
    if c.rowcount == 0:
        conn.close()
        return jsonify({"error": "Video not found"}), 404
    conn.commit()
    conn.close()
    return jsonify({"message": "Video deleted successfully"}), 200

@app.route('/videos/search', methods=['GET'])
def search_videos():
    query = request.args.get('q', '')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE title LIKE ? OR tags LIKE ?", (f'%{query}%', f'%{query}%'))
    videos = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
    conn.close()
    return jsonify(videos)

if __name__ == '__main__':
    app.run(host='localhost', port=7717, debug=True)
