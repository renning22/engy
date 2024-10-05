
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import math
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/calculate_weeks', methods=['POST'])
def calculate_weeks_route():
    birthdate = request.json.get('birthdate')
    if not birthdate:
        return jsonify({"error": "Birthdate is required"}), 400
    
    result = calculate_weeks(birthdate)
    return jsonify(result)

def calculate_weeks(birthdate):
    try:
        birth_date = datetime.strptime(birthdate, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    current_date = datetime.now()
    
    if birth_date > current_date:
        return {"error": "Birthdate cannot be in the future"}

    weeks_lived = math.floor((current_date - birth_date).days / 7)
    total_weeks_in_100_years = 100 * 52
    remaining_weeks = max(0, total_weeks_in_100_years - weeks_lived)

    return {
        "weeks_lived": weeks_lived,
        "total_weeks": total_weeks_in_100_years,
        "remaining_weeks": remaining_weeks
    }

if __name__ == '__main__':
    app.run(host='localhost', port=9825, debug=True)
