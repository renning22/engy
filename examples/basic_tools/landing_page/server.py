
from flask import Flask, send_file, jsonify
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

# Get the directory containing server.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """Serve index.html from the same directory as server.py"""
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/api/glitch-effect')
def glitch_effect():
    """API endpoint for glitch effect parameters"""
    return jsonify({
        'offset': random.randint(-5, 5),
        'opacity': random.uniform(0.8, 1.0)
    })

# Error handling for missing index.html
@app.errorhandler(404)
def not_found(e):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Not Found</title>
        <style>
            body {
                background-color: #0a0a0a;
                color: #00ff9d;
                font-family: monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }
            .error {
                padding: 20px;
                border: 1px solid #00ff9d;
            }
        </style>
    </head>
    <body>
        <div class="error">
            <h1>Error: index.html not found</h1>
            <p>Please ensure index.html exists in the same directory as server.py</p>
        </div>
    </body>
    </html>
    """, 404

# Custom error handler for other errors
@app.errorhandler(500)
def server_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    # Check if index.html exists
    if not os.path.exists(os.path.join(BASE_DIR, 'index.html')):
        print("Warning: index.html not found in the current directory!")
        print(f"Please ensure index.html exists in: {BASE_DIR}")
    
    # Start the server
    app.run(
        host='0.0.0.0',
        port=8933,
        debug=True
    )
