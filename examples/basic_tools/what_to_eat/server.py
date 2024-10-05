
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import random
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Mock database of top restaurants in SF Bay Area
restaurants = [
    {"id": 1, "name": "Golden Dragon", "genre": "Chinese", "rating": 4.5, "phone": "+1 (415) 123-4567", "website": "https://www.goldendragonsf.com", "address": "123 Main St, San Francisco, CA 94122"},
    {"id": 2, "name": "Taqueria El Farolito", "genre": "Mexican", "rating": 4.7, "phone": "+1 (415) 234-5678", "website": "https://www.elfarolitosf.com", "address": "456 Mission St, San Francisco, CA 94110"},
    {"id": 3, "name": "The Cheesecake Factory", "genre": "American", "rating": 4.2, "phone": "+1 (415) 345-6789", "website": "https://www.thecheesecakefactory.com", "address": "789 Market St, San Francisco, CA 94103"},
    {"id": 4, "name": "Sushi Ran", "genre": "Japanese", "rating": 4.8, "phone": "+1 (415) 456-7890", "website": "https://www.sushiran.com", "address": "101 Bridgeway, Sausalito, CA 94965"},
    {"id": 5, "name": "La Ciccia", "genre": "Italian", "rating": 4.6, "phone": "+1 (415) 567-8901", "website": "https://www.laciccia.com", "address": "291 30th St, San Francisco, CA 94131"},
    {"id": 6, "name": "Nopa", "genre": "American", "rating": 4.5, "phone": "+1 (415) 678-9012", "website": "https://www.nopasf.com", "address": "560 Divisadero St, San Francisco, CA 94117"},
    {"id": 7, "name": "Delfina", "genre": "Italian", "rating": 4.4, "phone": "+1 (415) 789-0123", "website": "https://www.delfinasf.com", "address": "3621 18th St, San Francisco, CA 94110"},
    {"id": 8, "name": "Burma Superstar", "genre": "Burmese", "rating": 4.3, "phone": "+1 (415) 890-1234", "website": "https://www.burmasuperstar.com", "address": "309 Clement St, San Francisco, CA 94118"},
    {"id": 9, "name": "House of Prime Rib", "genre": "American", "rating": 4.5, "phone": "+1 (415) 901-2345", "website": "https://www.houseofprimerib.net", "address": "1906 Van Ness Ave, San Francisco, CA 94109"},
    {"id": 10, "name": "Kokkari Estiatorio", "genre": "Greek", "rating": 4.6, "phone": "+1 (415) 012-3456", "website": "https://www.kokkari.com", "address": "200 Jackson St, San Francisco, CA 94111"},
    {"id": 11, "name": "Yank Sing", "genre": "Chinese", "rating": 4.3, "phone": "+1 (415) 123-4567", "website": "https://www.yanksing.com", "address": "49 Stevenson St, San Francisco, CA 94105"},
    {"id": 12, "name": "La Taqueria", "genre": "Mexican", "rating": 4.4, "phone": "+1 (415) 234-5678", "website": "https://www.lataqueriasf.com", "address": "2889 Mission St, San Francisco, CA 94110"},
    {"id": 13, "name": "Saigon Sandwich", "genre": "Vietnamese", "rating": 4.5, "phone": "+1 (415) 345-6789", "website": "https://www.saigonsandwichsf.com", "address": "560 Larkin St, San Francisco, CA 94102"},
    {"id": 14, "name": "Chez Panisse", "genre": "California Cuisine", "rating": 4.4, "phone": "+1 (510) 456-7890", "website": "https://www.chezpanisse.com", "address": "1517 Shattuck Ave, Berkeley, CA 94709"},
    {"id": 15, "name": "Atelier Crenn", "genre": "French", "rating": 4.7, "phone": "+1 (415) 567-8901", "website": "https://www.ateliercrenn.com", "address": "3127 Fillmore St, San Francisco, CA 94123"},
    {"id": 16, "name": "Benu", "genre": "Contemporary", "rating": 4.8, "phone": "+1 (415) 678-9012", "website": "https://www.benusf.com", "address": "22 Hawthorne St, San Francisco, CA 94105"},
    {"id": 17, "name": "State Bird Provisions", "genre": "American", "rating": 4.5, "phone": "+1 (415) 789-0123", "website": "https://www.statebirdsf.com", "address": "1529 Fillmore St, San Francisco, CA 94115"},
    {"id": 18, "name": "Coi", "genre": "Contemporary", "rating": 4.6, "phone": "+1 (415) 890-1234", "website": "https://www.coirestaurant.com", "address": "373 Broadway, San Francisco, CA 94133"},
    {"id": 19, "name": "Zuni Cafe", "genre": "California Cuisine", "rating": 4.3, "phone": "+1 (415) 901-2345", "website": "https://www.zunicafe.com", "address": "1658 Market St, San Francisco, CA 94102"},
    {"id": 20, "name": "Gary Danko", "genre": "Contemporary American", "rating": 4.7, "phone": "+1 (415) 012-3456", "website": "https://www.garydanko.com", "address": "800 N Point St, San Francisco, CA 94109"}
]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    return jsonify(restaurants)

@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
    if restaurant:
        return jsonify(restaurant)
    return jsonify({"error": "Restaurant not found"}), 404

@app.route('/restaurants/random', methods=['GET'])
def get_random_restaurant():
    return jsonify(random.choice(restaurants))

@app.route('/restaurants/genre/<string:genre>', methods=['GET'])
def get_restaurants_by_genre(genre):
    filtered_restaurants = [r for r in restaurants if r['genre'].lower() == genre.lower()]
    return jsonify(filtered_restaurants)

if __name__ == '__main__':
    app.run(host='localhost', port=5973, debug=True)
