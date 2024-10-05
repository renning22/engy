
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Mock data for schools in Fremont, CA
schools = [
    {
        "name": "Fremont High School",
        "address": "1279 Sunnyvale Saratoga Rd, Sunnyvale, CA 94087",
        "overall_rating": 8,
        "art_program_rating": 9,
        "art_program_description": "Comprehensive visual and performing arts program",
        "latitude": 37.3506,
        "longitude": -122.0075
    },
    {
        "name": "Mission San Jose High School",
        "address": "41717 Palm Ave, Fremont, CA 94539",
        "overall_rating": 9,
        "art_program_rating": 8,
        "art_program_description": "Strong emphasis on digital arts and music",
        "latitude": 37.5229,
        "longitude": -121.9179
    },
    {
        "name": "Irvington High School",
        "address": "41800 Blacow Rd, Fremont, CA 94538",
        "overall_rating": 8,
        "art_program_rating": 7,
        "art_program_description": "Diverse range of visual arts courses",
        "latitude": 37.5284,
        "longitude": -121.9636
    },
    {
        "name": "American High School",
        "address": "36300 Fremont Blvd, Fremont, CA 94536",
        "overall_rating": 7,
        "art_program_rating": 8,
        "art_program_description": "Innovative multimedia and design programs",
        "latitude": 37.5584,
        "longitude": -122.0067
    },
    {
        "name": "Washington High School",
        "address": "38442 Fremont Blvd, Fremont, CA 94536",
        "overall_rating": 7,
        "art_program_rating": 6,
        "art_program_description": "Traditional fine arts with a modern twist",
        "latitude": 37.5423,
        "longitude": -121.9867
    }
]

# Simple in-memory cache
cache = {}

def cache_for(seconds):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = f.__name__ + str(args) + str(kwargs)
            if key in cache:
                result, timestamp = cache[key]
                if datetime.now() - timestamp < timedelta(seconds=seconds):
                    return result
            result = f(*args, **kwargs)
            cache[key] = (result, datetime.now())
            return result
        return wrapper
    return decorator

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/schools')
@cache_for(300)  # Cache for 5 minutes
def get_schools():
    return jsonify(schools)

if __name__ == '__main__':
    app.run(host='localhost', port=7847)
