
import os
import docker
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='.')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Docker client
client = docker.from_env()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/containers', methods=['GET'])
def list_containers():
    try:
        containers = client.containers.list()
        container_list = [{
            'id': container.id,
            'name': container.name,
            'status': container.status,
            'image': container.image.tags,
            'created': container.attrs['Created'],
            'ports': container.ports
        } for container in containers]
        logging.info(f"Listed {len(container_list)} containers")
        return jsonify(container_list)
    except Exception as e:
        logging.error(f"Error listing containers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/container/<container_id>/kill', methods=['POST'])
def kill_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.kill()
        logging.info(f"Killed container {container_id}")
        socketio.emit('container_killed', {'container_id': container_id})
        return jsonify({'message': f'Container {container_id} killed successfully'})
    except Exception as e:
        logging.error(f"Error killing container {container_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/container/<container_id>/inspect', methods=['GET'])
def inspect_container(container_id):
    try:
        container = client.containers.get(container_id)
        inspection = container.attrs
        logging.info(f"Inspected container {container_id}")
        return jsonify(inspection)
    except Exception as e:
        logging.error(f"Error inspecting container {container_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/container/<container_id>/exec', methods=['POST'])
def exec_in_container(container_id):
    command = request.json.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    try:
        container = client.containers.get(container_id)
        result = container.exec_run(command)
        logging.info(f"Executed command in container {container_id}: {command}")
        return jsonify({
            'exit_code': result.exit_code,
            'output': result.output.decode('utf-8')
        })
    except Exception as e:
        logging.error(f"Error executing command in container {container_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    logging.info(f"WebSocket client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info(f"WebSocket client disconnected: {request.sid}")

def monitor_containers():
    for event in client.events(decode=True):
        if event['Type'] == 'container':
            socketio.emit('container_event', event)

if __name__ == '__main__':
    from threading import Thread
    container_monitor = Thread(target=monitor_containers)
    container_monitor.start()
    socketio.run(app, host='localhost', port=5494, debug=True)
