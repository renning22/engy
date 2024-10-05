
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Mock data to simulate Airtable contacts
mock_contacts = [
    {"id": "1", "name": "John Doe", "email": "john@example.com"},
    {"id": "2", "name": "Jane Smith", "email": "jane@example.com"},
    {"id": "3", "name": "Bob Johnson", "email": "bob@example.com"},
]

# Mock function to simulate getting contacts from Airtable
def get_contacts():
    return mock_contacts

# Mock function to simulate sending an email
def send_email(recipient, subject, body):
    print(f"Sending email to: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/contacts', methods=['GET'])
def contacts():
    return jsonify(get_contacts())

@app.route('/send-email', methods=['POST'])
def send_email_route():
    data = request.json
    recipient = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')

    if not all([recipient, subject, body]):
        return jsonify({"error": "Missing required fields"}), 400

    success = send_email(recipient, subject, body)
    if success:
        return jsonify({"message": "Email sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send email"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=8580, debug=True)
