from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# In-memory database
got_db = {
    "characters": [
        {"id": 1, "name": "Jon Snow", "house": "Stark", "country": "The North"},
        {"id": 2, "name": "Daenerys Targaryen", "house": "Targaryen", "country": "Essos"},
        {"id": 3, "name": "Tyrion Lannister", "house": "Lannister", "country": "The Westerlands"},
        {"id": 4, "name": "Arya Stark", "house": "Stark", "country": "The North"},
        {"id": 5, "name": "Cersei Lannister", "house": "Lannister", "country": "The Westerlands"}
    ],
    "countries": [
        {"id": 1, "name": "The North", "capital": "Winterfell"},
        {"id": 2, "name": "The Westerlands", "capital": "Casterly Rock"},
        {"id": 3, "name": "The Reach", "capital": "Highgarden"},
        {"id": 4, "name": "Dorne", "capital": "Sunspear"},
        {"id": 5, "name": "Essos", "capital": "Various city-states"}
    ]
}

# Routes
@app.route('/characters', methods=['GET'])
def get_characters():
    return jsonify(got_db["characters"])

@app.route('/characters/<int:char_id>', methods=['GET'])
def get_character(char_id):
    character = next((char for char in got_db["characters"] if char["id"] == char_id), None)
    if character:
        return jsonify(character)
    return jsonify({"error": "Character not found"}), 404

@app.route('/countries', methods=['GET'])
def get_countries():
    return jsonify(got_db["countries"])

@app.route('/countries/<int:country_id>', methods=['GET'])
def get_country(country_id):
    country = next((country for country in got_db["countries"] if country["id"] == country_id), None)
    if country:
        return jsonify(country)
    return jsonify({"error": "Country not found"}), 404

@app.route('/characters', methods=['POST'])
def add_character():
    new_character = request.json
    new_character["id"] = max(char["id"] for char in got_db["characters"]) + 1
    got_db["characters"].append(new_character)
    return jsonify(new_character), 201

@app.route('/countries', methods=['POST'])
def add_country():
    new_country = request.json
    new_country["id"] = max(country["id"] for country in got_db["countries"]) + 1
    got_db["countries"].append(new_country)
    return jsonify(new_country), 201

if __name__ == '__main__':
    app.run(debug=True)