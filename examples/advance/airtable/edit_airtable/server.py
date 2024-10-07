
import os
from flask import Flask, request, jsonify, session, send_file, send_from_directory
from flask_cors import CORS
import requests
import pandas as pd
from io import StringIO
import json

app = Flask(__name__, static_folder='.')
app.secret_key = os.urandom(24)
CORS(app)

AIRTABLE_API_URL = "https://api.airtable.com/v0"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    api_key = data.get('api_key')
    base_id = data.get('base_id')
    
    if not api_key or not base_id:
        return jsonify({"error": "API key and base ID are required"}), 400
    
    try:
        # Test connection and fetch table data
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{AIRTABLE_API_URL}/{base_id}", headers=headers)
        response.raise_for_status()
        
        # Store connection details and table data in session
        session['api_key'] = api_key
        session['base_id'] = base_id
        session['table_data'] = response.json()
        
        return jsonify({"message": "Connected successfully", "data": session['table_data']}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect: {str(e)}"}), 400

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    if 'api_key' not in session or 'base_id' not in session:
        return jsonify({"error": "Not connected to Airtable"}), 401
    
    try:
        data = fetch_table_data()
        session['table_data'] = data
        return jsonify(data), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 400

@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    updated_data = data.get('data')
    
    if not updated_data:
        return jsonify({"error": "Data is required"}), 400
    
    if 'api_key' not in session or 'base_id' not in session:
        return jsonify({"error": "Not connected to Airtable"}), 401
    
    try:
        result = update_table_data(updated_data)
        return jsonify(result), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to update data: {str(e)}"}), 400

@app.route('/export_csv', methods=['GET'])
def export_csv():
    if 'table_data' not in session:
        return jsonify({"error": "No table data available"}), 400
    
    try:
        csv_data = export_to_csv(session['table_data'])
        return send_file(
            StringIO(csv_data),
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='table_export.csv'
        )
    except Exception as e:
        return jsonify({"error": f"Failed to export CSV: {str(e)}"}), 400

def fetch_table_data():
    headers = {
        "Authorization": f"Bearer {session['api_key']}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{AIRTABLE_API_URL}/{session['base_id']}", headers=headers)
    response.raise_for_status()
    return response.json()

def update_table_data(data):
    headers = {
        "Authorization": f"Bearer {session['api_key']}",
        "Content-Type": "application/json"
    }
    response = requests.patch(
        f"{AIRTABLE_API_URL}/{session['base_id']}",
        headers=headers,
        json={"records": data}
    )
    response.raise_for_status()
    return response.json()

def export_to_csv(data):
    df = pd.DataFrame(data['records'])
    df['fields'] = df['fields'].apply(json.dumps)
    return df.to_csv(index=False)

if __name__ == '__main__':
    app.run(host='localhost', port=8369, debug=True)
