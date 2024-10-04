
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from agents import all_agents
import threading
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store execution status and results
execution_status = {}
execution_results = {}

def execute_agent(agent_name):
    agent = next((a for a in all_agents if a.name == agent_name), None)
    if agent:
        execution_status[agent_name] = "Running"
        socketio.emit('status_update', {'agent': agent_name, 'status': "Running"})
        
        try:
            result = agent.execute()
            execution_results[agent_name] = result
            execution_status[agent_name] = "Completed"
            socketio.emit('status_update', {'agent': agent_name, 'status': "Completed"})
            socketio.emit('execution_result', {'agent': agent_name, 'result': result})
        except Exception as e:
            execution_status[agent_name] = f"Error: {str(e)}"
            socketio.emit('status_update', {'agent': agent_name, 'status': f"Error: {str(e)}"})
    else:
        socketio.emit('status_update', {'agent': agent_name, 'status': "Agent not found"})

@app.route('/api/execute/<agent_name>', methods=['POST'])
def execute_agent_api(agent_name):
    threading.Thread(target=execute_agent, args=(agent_name,)).start()
    return jsonify({"message": f"Execution of {agent_name} started"}), 202

@app.route('/api/agents', methods=['GET'])
def get_agents_metadata():
    agents_metadata = []
    for agent in all_agents:
        agents_metadata.append({
            "name": agent.name,
            "role": agent.role,
            "send_to": agent.send_to,
            "receive_from": agent.receive_from
        })
    return jsonify(agents_metadata)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_status')
def handle_subscribe_status():
    for agent_name, status in execution_status.items():
        emit('status_update', {'agent': agent_name, 'status': status})

@socketio.on('subscribe_results')
def handle_subscribe_results():
    for agent_name, result in execution_results.items():
        emit('execution_result', {'agent': agent_name, 'result': result})

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=8314, debug=True)
