crew_ai_code_example = '''

import os
import threading
import time

from crewai import Agent, Crew, Task
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.agents import AgentFinish

app = Flask(__name__, static_folder='.')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage
search_results = {}
step_logs = {}

model = 'claude-3-5-sonnet-20240620'
os.environ["ANTHROPIC_API_KEY"] = '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'
llm = ChatAnthropic(model=model, temperature=0.2)

# CrewAI Agents
person_searcher = Agent(
    role='Person Searcher',
    goal='Find basic information about a person',
    backstory='You are an expert at finding general information about people online.',
    tools=[DuckDuckGoSearchRun()],
    llm=llm
)

contact_finder = Agent(
    role='Contact Finder',
    goal='Find email addresses and additional details about a person',
    backstory='You are skilled at uncovering contact information and additional details about individuals.',
    tools=[DuckDuckGoSearchRun()],
    llm=llm
)

def update_step_log(name, step, message):
    if name not in step_logs:
        step_logs[name] = []
    step_logs[name].append({"step": step, "message": message})
    socketio.emit('step_update', {"name": name, "step": step, "message": message})

def research_person(name):
    def step_callback(step_output):
        output = step_output
        if isinstance(output, AgentFinish):
            st = f"""{output.type}({list(output.return_values.keys())})"""
            update_step_log(name, output.type, st)
        else:
            assert isinstance(output, list)
            for action, observation in output:
                st = f"""{action.type}(tool='{action.tool}', tool_input='{action.tool_input}', observation={len(observation)})"""
                update_step_log(name, f"{action.type}(tool='{action.tool}'", st)

    crew = Crew(
        agents=[person_searcher, contact_finder],
        tasks=[
            Task(
                description=f"Find basic information about {name}",
                expected_output='Pure texts',
                agent=person_searcher
            ),
            Task(
                description=f"Find email addresses and additional details about {name}",
                expected_output='Pure texts',
                agent=contact_finder
            )
        ],
        step_callback=step_callback
    )

    result = crew.kickoff()
    return str(result)


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400

    def run_search():
        update_step_log(name, "Started", f"Initiating search for {name}")
        try:
            result = research_person(name)
            search_results[name] = result
            update_step_log(name, "Completed", f"Search completed for {name}")
        except Exception as e:
            update_step_log(name, "Error", f"An error occurred: {str(e)}")

    threading.Thread(target=run_search).start()
    return jsonify({"message": f"Search initiated for {name}"}), 202

@app.route('/status', methods=['GET'])
def status():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400

    result = search_results.get(name)
    logs = step_logs.get(name, [])

    return jsonify({
        "name": name,
        "result": result,
        "logs": logs,
        "status": "Completed" if result else "In Progress"
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5286, debug=True)
'''