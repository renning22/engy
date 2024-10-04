
import os
import json
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Thread
from agents import research_and_write_report

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for simplicity
research_jobs = {}
agents = [
    {"name": "Dr. Amelia Reeves", "role": "Research Director"},
    {"name": "Lucas Ortiz", "role": "Data Scientist"},
    {"name": "Zara Chen", "role": "Research Analyst"},
    {"name": "Oliver Nkosi", "role": "Insights Specialist"},
    {"name": "Sophia Larsson", "role": "Technical Writer"},
    {"name": "Dr. Rajesh Patel", "role": "Scientific Reviewer"},
    {"name": "Emma Dubois", "role": "Data Visualization Specialist"}
]

workflow = [
    "Define research scope",
    "Conduct literature review",
    "Design and conduct primary research",
    "Analyze primary data",
    "Synthesize findings",
    "Create data visualizations",
    "Develop report outline",
    "Write first draft",
    "Review for scientific rigor",
    "Incorporate feedback",
    "Design final layout",
    "Conduct final review"
]

def get_agent_for_step(step):
    # Map steps to agents (you may need to adjust this based on your actual workflow)
    step_agent_map = {
        1: "Dr. Amelia Reeves",
        2: "Zara Chen",
        3: "Lucas Ortiz",
        4: "Lucas Ortiz",
        5: "Oliver Nkosi",
        6: "Emma Dubois",
        7: "Sophia Larsson",
        8: "Sophia Larsson",
        9: "Dr. Rajesh Patel",
        10: "Sophia Larsson",
        11: "Emma Dubois",
        12: "Dr. Amelia Reeves"
    }
    return step_agent_map.get(step, "Unknown Agent")

def run_research(job_id, topic):
    research_jobs[job_id]['status'] = 'in_progress'
    socketio.emit('research_update', {'job_id': job_id, 'status': 'in_progress'})

    def update_status(data):
        current_step = research_jobs[job_id].get('current_step', 0) + 1
        current_agent = get_agent_for_step(current_step)
        research_jobs[job_id]['current_step'] = current_step
        research_jobs[job_id]['current_agent'] = current_agent
        socketio.emit('research_update', {
            'job_id': job_id,
            'status': data['status'],
            'result': data['result'],
            'current_step': current_step,
            'total_steps': len(workflow),
            'step_description': workflow[current_step - 1],
            'current_agent': current_agent
        })

    result = research_and_write_report(topic, update_status)
    research_jobs[job_id]['status'] = 'completed'
    research_jobs[job_id]['result'] = result
    socketio.emit('research_update', {
        'job_id': job_id,
        'status': 'completed',
        'result': result,
        'current_step': len(workflow),
        'total_steps': len(workflow),
        'current_agent': None
    })

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/research', methods=['POST'])
def start_research():
    topic = request.json['topic']
    job_id = str(uuid.uuid4())
    research_jobs[job_id] = {'status': 'pending', 'topic': topic}
    Thread(target=run_research, args=(job_id, topic)).start()
    return jsonify({'job_id': job_id}), 202

@app.route('/api/research/<job_id>/status', methods=['GET'])
def get_research_status(job_id):
    job = research_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({
        'status': job['status'],
        'current_step': job.get('current_step', 0),
        'total_steps': len(workflow),
        'current_agent': job.get('current_agent')
    })

@app.route('/api/research/<job_id>/results', methods=['GET'])
def get_research_results(job_id):
    job = research_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if job['status'] != 'completed':
        return jsonify({'error': 'Research not completed yet'}), 400
    return jsonify({'results': job['result']})

@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify(agents)

@app.route('/api/workflow', methods=['GET'])
def get_workflow():
    return jsonify(workflow)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5901, debug=True)
