
import os
import subprocess
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import paramiko
from functools import wraps

app = Flask(__name__, static_folder='.')
CORS(app)

# Simple in-memory user database (replace with a more secure solution in production)
USERS = {
    "admin": "password123"
}

def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    return username in USERS and USERS[username] == password

def run_kubectl_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/nodes', methods=['GET'])
@authenticate
def get_nodes():
    output = run_kubectl_command(["kubectl", "get", "nodes", "-o", "json"])
    nodes = json.loads(output)
    return jsonify(nodes)

@app.route('/pods', methods=['GET'])
@authenticate
def get_pods():
    output = run_kubectl_command(["kubectl", "get", "pods", "--all-namespaces", "-o", "json"])
    pods = json.loads(output)
    return jsonify(pods)

@app.route('/ssh', methods=['POST'])
@authenticate
def ssh_command():
    data = request.json
    if not data or 'target' not in data or 'command' not in data:
        return jsonify({"error": "Invalid request"}), 400

    target = data['target']
    command = data['command']

    # In a real scenario, you'd need to securely manage SSH keys and connection details
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(target, username='user', key_filename='/path/to/private/key')
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ssh.close()

@app.route('/kill', methods=['POST'])
@authenticate
def kill_pod():
    data = request.json
    if not data or 'pod_name' not in data:
        return jsonify({"error": "Invalid request"}), 400

    pod_name = data['pod_name']
    try:
        output = run_kubectl_command(["kubectl", "delete", "pod", pod_name])
        return jsonify({"status": "success", "output": output})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "failure", "error": str(e)}), 500

@app.route('/details/<resource_type>/<name>', methods=['GET'])
@authenticate
def get_resource_details(resource_type, name):
    allowed_types = ['node', 'pod', 'service', 'deployment']
    if resource_type not in allowed_types:
        return jsonify({"error": "Invalid resource type"}), 400

    try:
        output = run_kubectl_command(["kubectl", "describe", resource_type, name])
        return jsonify({"details": output})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=6478)
