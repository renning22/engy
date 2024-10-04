
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient import discovery
import json

app = Flask(__name__, static_folder='.')
CORS(app)

# Mock data for demonstration purposes
MOCK_INSTANCES = [
    {"name": "instance-1", "status": "RUNNING", "zone": "us-central1-a"},
    {"name": "instance-2", "status": "STOPPED", "zone": "us-central1-b"},
    {"name": "instance-3", "status": "RUNNING", "zone": "us-west1-a"},
]

# Helper function to get Compute Engine client
def get_compute_client():
    # In a real scenario, you would use actual credentials
    # credentials = service_account.Credentials.from_service_account_file('path/to/service_account.json')
    # return discovery.build('compute', 'v1', credentials=credentials)
    
    # For this mock implementation, we'll return None
    return None

# Helper function to list instances
def list_instances():
    # In a real scenario, you would fetch actual instance data from GCP
    # client = get_compute_client()
    # result = client.instances().list(project='your-project-id', zone='your-zone').execute()
    # return result.get('items', [])
    
    # For this mock implementation, we'll return the mock data
    return MOCK_INSTANCES

# Helper function to stop an instance
def stop_instance(name, zone):
    # In a real scenario, you would use the Compute Engine API to stop the instance
    # client = get_compute_client()
    # operation = client.instances().stop(project='your-project-id', zone=zone, instance=name).execute()
    # return operation
    
    # For this mock implementation, we'll just update the status in our mock data
    for instance in MOCK_INSTANCES:
        if instance['name'] == name and instance['zone'] == zone:
            instance['status'] = 'STOPPED'
            return True
    return False

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/instances', methods=['GET'])
def get_instances():
    try:
        instances = list_instances()
        return jsonify(instances), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ssh', methods=['POST'])
def generate_ssh_command():
    data = request.json
    instance_name = data.get('name')
    zone = data.get('zone')
    
    if not instance_name or not zone:
        return jsonify({"error": "Instance name and zone are required"}), 400
    
    # In a real scenario, you might need to fetch the external IP of the instance
    # For this mock implementation, we'll use a placeholder IP
    ssh_command = f"gcloud compute ssh {instance_name} --zone={zone}"
    
    return jsonify({"ssh_command": ssh_command}), 200

@app.route('/kill', methods=['POST'])
def kill_instance():
    data = request.json
    instance_name = data.get('name')
    zone = data.get('zone')
    
    if not instance_name or not zone:
        return jsonify({"error": "Instance name and zone are required"}), 400
    
    try:
        success = stop_instance(instance_name, zone)
        if success:
            return jsonify({"message": f"Instance {instance_name} stopped successfully"}), 200
        else:
            return jsonify({"error": f"Failed to stop instance {instance_name}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=6183, debug=True)
