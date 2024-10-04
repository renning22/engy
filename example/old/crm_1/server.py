
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import uuid
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# In-memory database
customers = [
    {"id": "1", "name": "John Doe", "company": "Acme Inc.", "email": "john.doe@acme.com", "sex": "Male", "sent": False},
    {"id": "2", "name": "Jane Smith", "company": "TechCorp", "email": "jane.smith@techcorp.com", "sex": "Female", "sent": False},
    {"id": "3", "name": "Bob Johnson", "company": "InnoSoft", "email": "bob.johnson@innosoft.com", "sex": "Male", "sent": False},
]

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/customers', methods=['GET'])
def get_customers():
    return jsonify(customers)

@app.route('/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = next((c for c in customers if c['id'] == customer_id), None)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.json
    new_customer = {
        "id": str(uuid.uuid4()),
        "name": data.get('name'),
        "company": data.get('company'),
        "email": data.get('email'),
        "sex": data.get('sex'),
        "sent": False
    }
    customers.append(new_customer)
    return jsonify(new_customer), 201

@app.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = next((c for c in customers if c['id'] == customer_id), None)
    if customer:
        data = request.json
        customer.update({
            "name": data.get('name', customer['name']),
            "company": data.get('company', customer['company']),
            "email": data.get('email', customer['email']),
            "sex": data.get('sex', customer['sex']),
            "sent": data.get('sent', customer['sent'])
        })
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/<string:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    global customers
    customers = [c for c in customers if c['id'] != customer_id]
    return '', 204

if __name__ == '__main__':
    app.run(host='localhost', port=8605, debug=True)
