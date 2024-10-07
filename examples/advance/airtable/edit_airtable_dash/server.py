
import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import requests
import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output, State
import io

class AirtableManager:
    def __init__(self, api_key, base_id, table_name):
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"

    def get_table_data(self):
        response = requests.get(self.base_url, headers=self.headers)
        return response.json()['records']

    def update_record(self, record_id, fields):
        url = f"{self.base_url}/{record_id}"
        data = {"fields": fields}
        response = requests.patch(url, json=data, headers=self.headers)
        return response.json()

    def sync_data(self):
        return self.get_table_data()

app = Flask(__name__)
CORS(app)
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')

airtable_manager = None

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/init', methods=['POST'])
def init_airtable():
    global airtable_manager
    data = request.json
    api_key = data.get('api_key')
    base_id = data.get('base_id')
    table_name = data.get('table_name')
    
    if not all([api_key, base_id, table_name]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    airtable_manager = AirtableManager(api_key, base_id, table_name)
    return jsonify({"message": "Airtable connection initialized"}), 200

@app.route('/api/get_data', methods=['GET'])
def get_data():
    if not airtable_manager:
        return jsonify({"error": "Airtable connection not initialized"}), 400
    
    data = airtable_manager.get_table_data()
    return jsonify(data), 200

@app.route('/api/update_record', methods=['POST'])
def update_record():
    if not airtable_manager:
        return jsonify({"error": "Airtable connection not initialized"}), 400
    
    data = request.json
    record_id = data.get('id')
    fields = data.get('fields')
    
    if not record_id or not fields:
        return jsonify({"error": "Missing record_id or fields"}), 400
    
    updated_record = airtable_manager.update_record(record_id, fields)
    return jsonify(updated_record), 200

@app.route('/api/export_csv', methods=['GET'])
def export_csv():
    if not airtable_manager:
        return jsonify({"error": "Airtable connection not initialized"}), 400
    
    data = airtable_manager.get_table_data()
    df = pd.DataFrame([record['fields'] for record in data])
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='airtable_data.csv'
    )

# Dash app layout and callbacks
dash_app.layout = html.Div([
    html.H1("Airtable Data Dashboard", className="text-3xl font-bold mb-4"),
    html.Div([
        html.Button("Refresh Data", id="refresh-button", className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2"),
        html.Button("Export CSV", id="export-csv-button", className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"),
    ], className="mb-4"),
    dash_table.DataTable(
        id='data-table',
        columns=[],
        data=[],
        editable=True,
        row_deletable=True,
        style_table={'overflowX': 'auto'},
        style_cell={
            'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=10,
    ),
])

@dash_app.callback(
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Input('refresh-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_dashboard(n_clicks):
    if not airtable_manager:
        return [], []
    
    data = airtable_manager.get_table_data()
    df = pd.DataFrame([{**record['fields'], 'id': record['id']} for record in data])
    
    columns = [{"name": i, "id": i} for i in df.columns]
    
    return df.to_dict('records'), columns

@dash_app.callback(
    Output('data-table', 'data', allow_duplicate=True),
    Input('data-table', 'data_timestamp'),
    State('data-table', 'data'),
    prevent_initial_call=True
)
def sync_with_airtable(timestamp, data):
    if not airtable_manager:
        return data

    for record in data:
        record_id = record.pop('id', None)
        if record_id:
            airtable_manager.update_record(record_id, record)

    return data

@dash_app.callback(
    Output('export-csv-button', 'n_clicks'),
    Input('export-csv-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_csv_callback(n_clicks):
    if n_clicks:
        return export_csv()
    return None

if __name__ == '__main__':
    app.run(host='localhost', port=6860, debug=True)
