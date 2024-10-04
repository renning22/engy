
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

# Mock data for restaurants
mock_restaurants = [
    {
        "name": "Golden Dragon",
        "address": "123 Main St, San Francisco, CA 94122",
        "rating": 4.5,
        "price": "$$",
        "phone": "+1 (415) 555-1234",
        "image_url": "https://example.com/golden-dragon.jpg",
        "yelp_url": "https://www.yelp.com/biz/golden-dragon-san-francisco"
    },
    {
        "name": "Sichuan Spice",
        "address": "456 Market St, San Jose, CA 95113",
        "rating": 4.2,
        "price": "$$$",
        "phone": "+1 (408) 555-5678",
        "image_url": "https://example.com/sichuan-spice.jpg",
        "yelp_url": "https://www.yelp.com/biz/sichuan-spice-san-jose"
    },
    {
        "name": "Dim Sum Palace",
        "address": "789 Broadway, Oakland, CA 94607",
        "rating": 4.7,
        "price": "$$",
        "phone": "+1 (510) 555-9012",
        "image_url": "https://example.com/dim-sum-palace.jpg",
        "yelp_url": "https://www.yelp.com/biz/dim-sum-palace-oakland"
    }
]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get_restaurant')
def get_restaurant():
    try:
        # Randomly select a restaurant from the mock data
        restaurant = random.choice(mock_restaurants)
        return jsonify(restaurant)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5816, debug=True)
