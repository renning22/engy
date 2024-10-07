
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import random
import string

app = Flask(__name__, static_folder='.')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/server.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/customers', methods=['GET'])
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'customers': [{'id': c.id, 'name': c.name, 'email': c.email} for c in customers.items],
        'total': customers.total,
        'pages': customers.pages,
        'current_page': page
    })

@app.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({'id': customer.id, 'name': customer.name, 'email': customer.email})

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json
    if not data or not 'name' in data or not 'email' in data:
        return jsonify({'error': 'Bad request'}), 400
    customer = Customer(name=data['name'], email=data['email'])
    db.session.add(customer)
    db.session.commit()
    app.logger.info(f'New customer created: {customer.id}')
    return jsonify({'id': customer.id, 'name': customer.name, 'email': customer.email}), 201

@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.json
    if 'name' in data:
        customer.name = data['name']
    if 'email' in data:
        customer.email = data['email']
    db.session.commit()
    app.logger.info(f'Customer updated: {customer.id}')
    return jsonify({'id': customer.id, 'name': customer.name, 'email': customer.email})

@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    app.logger.info(f'Customer deleted: {id}')
    return '', 204

@app.route('/api/customers/search', methods=['GET'])
def search_customers():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    customers = Customer.query.filter(
        (Customer.name.like(f'%{query}%')) | (Customer.email.like(f'%{query}%'))
    ).all()
    return jsonify([{'id': c.id, 'name': c.name, 'email': c.email} for c in customers])

@app.route('/api/generate_random_customers', methods=['POST'])
def generate_random_customers():
    count = request.json.get('count', 10)
    for _ in range(count):
        name = ''.join(random.choices(string.ascii_letters, k=10))
        email = f'{name.lower()}@example.com'
        customer = Customer(name=name, email=email)
        db.session.add(customer)
    db.session.commit()
    app.logger.info(f'{count} random customers generated')
    return jsonify({'message': f'{count} random customers generated successfully'}), 201

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', port=5198, debug=True)
