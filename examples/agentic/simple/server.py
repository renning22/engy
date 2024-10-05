
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from litellm import completion

app = Flask(__name__, static_folder='.')
CORS(app)

# LiteLLM setup
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
if not os.environ["ANTHROPIC_API_KEY"]:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# Database setup
DB_NAME = "search_history.db"

# Token pricing (per 1000 tokens)
INPUT_PRICE_PER_1K = 0.00025  # $0.00025 per 1K input tokens
OUTPUT_PRICE_PER_1K = 0.00125  # $0.00125 per 1K output tokens

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            cost REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Database operations
def add_to_history(query, response, input_tokens, output_tokens, cost):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_history (query, response, input_tokens, output_tokens, cost) VALUES (?, ?, ?, ?, ?)",
        (query, response, input_tokens, output_tokens, cost)
    )
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_history ORDER BY timestamp DESC")
    history = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "query": row[1],
            "response": row[2],
            "input_tokens": row[3],
            "output_tokens": row[4],
            "cost": row[5],
            "timestamp": row[6]
        } for row in history
    ]

def get_total_cost():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(cost) FROM search_history")
    total_cost = cursor.fetchone()[0] or 0
    conn.close()
    return total_cost

# LLM integration using LiteLLM
def query_llm(prompt):
    try:
        response = completion(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip()
        
        # Calculate costs
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        input_cost = (input_tokens / 1000) * INPUT_PRICE_PER_1K
        output_cost = (output_tokens / 1000) * OUTPUT_PRICE_PER_1K
        total_cost = input_cost + output_cost

        return content, input_tokens, output_tokens, total_cost
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return "Sorry, I encountered an error while processing your request.", 0, 0, 0

# API endpoints
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    response, input_tokens, output_tokens, cost = query_llm(query)
    add_to_history(query, response, input_tokens, output_tokens, cost)
    
    return jsonify({
        "response": response,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost
    })

@app.route('/history', methods=['GET'])
def history():
    return jsonify(get_history())

@app.route('/total_cost', methods=['GET'])
def total_cost():
    return jsonify({"total_cost": get_total_cost()})

# Serve static files (CSS, JS, images, etc.)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='localhost', port=7179, debug=True)
