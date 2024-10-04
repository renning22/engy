
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# In-memory database
crm_versions = [
    {"id": 1, "version": "1.0.0", "release_date": "2023-01-15"},
    {"id": 2, "version": "1.1.0", "release_date": "2023-06-30"},
    {"id": 3, "version": "2.0.0", "release_date": "2024-01-10"}
]

customers = [
    {
        "id": 1,
        "name": "Acme Corp",
        "contact": "John Doe",
        "email": "john.doe@acme.com",
        "phone": "+1 (555) 123-4567",
        "current_version": "1.1.0"
    },
    {
        "id": 2,
        "name": "TechSolutions Inc",
        "contact": "Jane Smith",
        "email": "jane.smith@techsolutions.com",
        "phone": "+1 (555) 987-6543",
        "current_version": "2.0.0"
    },
    {
        "id": 3,
        "name": "Global Enterprises",
        "contact": "Bob Johnson",
        "email": "bob.johnson@globalent.com",
        "phone": "+1 (555) 246-8135",
        "current_version": "1.0.0"
    }
]

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/versions', methods=['GET'])
def get_versions():
    return jsonify(crm_versions)

@app.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(customers)

@app.route('/api/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = next((c for c in customers if c['id'] == customer_id), None)
    if customer:
        return jsonify(customer)
    else:
        return jsonify({"error": "Customer not found"}), 404

@app.route('/api/customer/<int:customer_id>/version', methods=['GET'])
def get_customer_version(customer_id):
    customer = next((c for c in customers if c['id'] == customer_id), None)
    if customer:
        return jsonify({"current_version": customer['current_version']})
    else:
        return jsonify({"error": "Customer not found"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=9878, debug=True)
