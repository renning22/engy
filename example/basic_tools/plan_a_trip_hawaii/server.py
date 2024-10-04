
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Mock database for Hawaii attractions and activities
hawaii_data = {
    "attractions": [
        {"id": 1, "name": "Waikiki Beach", "location": "Oahu", "type": "Beach"},
        {"id": 2, "name": "Hawaii Volcanoes National Park", "location": "Big Island", "type": "Nature"},
        {"id": 3, "name": "Haleakala National Park", "location": "Maui", "type": "Nature"},
        {"id": 4, "name": "Pearl Harbor National Memorial", "location": "Oahu", "type": "Historical"},
        {"id": 5, "name": "Na Pali Coast", "location": "Kauai", "type": "Nature"},
    ],
    "activities": [
        {"id": 1, "name": "Surfing Lessons", "location": "Oahu", "type": "Water Sports"},
        {"id": 2, "name": "Luau Show", "location": "Maui", "type": "Cultural"},
        {"id": 3, "name": "Helicopter Tour", "location": "Big Island", "type": "Adventure"},
        {"id": 4, "name": "Snorkeling", "location": "Kauai", "type": "Water Sports"},
        {"id": 5, "name": "Hiking", "location": "Oahu", "type": "Nature"},
    ]
}

def generate_trip_plan(start_date, duration, preferences):
    trip_plan = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    for _ in range(duration):
        day_plan = {
            "date": current_date.strftime("%Y-%m-%d"),
            "activities": []
        }

        # Add 1-3 activities/attractions per day
        num_activities = random.randint(1, 3)
        for _ in range(num_activities):
            if random.choice([True, False]):
                item = random.choice(hawaii_data["attractions"])
            else:
                item = random.choice(hawaii_data["activities"])
            
            day_plan["activities"].append(item)

        trip_plan.append(day_plan)
        current_date += timedelta(days=1)

    return trip_plan

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/plan', methods=['POST'])
def plan_trip():
    try:
        data = request.json
        start_date = data.get('start_date')
        duration = int(data.get('duration', 7))
        preferences = data.get('preferences', [])

        if not start_date:
            return jsonify({"error": "Start date is required"}), 400

        trip_plan = generate_trip_plan(start_date, duration, preferences)
        return jsonify({"trip_plan": trip_plan})

    except Exception as e:
        app.logger.error(f"Error in plan_trip: {str(e)}")
        return jsonify({"error": "An error occurred while planning the trip"}), 500

@app.route('/attractions', methods=['GET'])
def get_attractions():
    return jsonify(hawaii_data["attractions"])

@app.route('/activities', methods=['GET'])
def get_activities():
    return jsonify(hawaii_data["activities"])

if __name__ == '__main__':
    app.run(host='localhost', port=7399, debug=True)
