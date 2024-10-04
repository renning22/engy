
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# In-memory database of countries
countries = [
    {"id": 1, "name": "United States", "population": 331002651, "location": "North America", "language": "English"},
    {"id": 2, "name": "China", "population": 1439323776, "location": "East Asia", "language": "Mandarin"},
    {"id": 3, "name": "India", "population": 1380004385, "location": "South Asia", "language": "Hindi"},
    {"id": 4, "name": "Brazil", "population": 212559417, "location": "South America", "language": "Portuguese"},
    {"id": 5, "name": "Russia", "population": 145934462, "location": "Eastern Europe", "language": "Russian"},
]

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/countries', methods=['GET'])
def get_countries():
    return jsonify(countries)

@app.route('/countries/<int:country_id>', methods=['GET'])
def get_country(country_id):
    country = next((c for c in countries if c['id'] == country_id), None)
    if country:
        return jsonify(country)
    return jsonify({"error": "Country not found"}), 404

@app.route('/countries', methods=['POST'])
def add_country():
    new_country = request.json
    new_country['id'] = max(c['id'] for c in countries) + 1
    countries.append(new_country)
    return jsonify(new_country), 201

@app.route('/countries/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    country = next((c for c in countries if c['id'] == country_id), None)
    if country:
        country.update(request.json)
        return jsonify(country)
    return jsonify({"error": "Country not found"}), 404

@app.route('/countries/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    global countries
    countries = [c for c in countries if c['id'] != country_id]
    return '', 204

@app.route('/countries/search', methods=['GET'])
def search_countries():
    query = request.args.get('q', '').lower()
    results = [c for c in countries if query in c['name'].lower() or query in c['location'].lower() or query in c['language'].lower()]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='localhost', port=7668, debug=True)
