
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load configuration
with open('config.json', 'r') as config_file:
    agents_config = json.load(config_file)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get_agents')
def get_agents():
    return jsonify(agents_config)

if __name__ == '__main__':
    app.run(host='localhost', port=7509, debug=True)
