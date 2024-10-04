
import os
import uuid
from threading import Thread

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.agents import AgentFinish
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Assume ANTHROPIC_API_KEY and other keys have been set in .env file.
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up the language model
model = 'claude-3-haiku-20240307'
llm = ChatAnthropic(model=model, temperature=0.2)

# Initialize tools
duck_tool = DuckDuckGoSearchRun()
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Create agents
alex_dataminer = Agent(
    role='Data Miner',
    goal='Gather and analyze data on recent YC accepted applications',
    backstory='Former data scientist at a top tech company, Alex specializes in collecting and analyzing large datasets. They have a keen eye for patterns and trends in startup ecosystems.',
    tools=[search_tool, scrape_tool],
    llm=llm
)

samantha_ycinsider = Agent(
    role='YC Insider',
    goal='Provide insights on YC selection criteria and preferences',
    backstory='Ex-YC partner with years of experience in evaluating startup applications. Samantha has a deep understanding of what YC looks for in potential investments.',
    tools=[search_tool],
    llm=llm
)

marcus_trendspotter = Agent(
    role='Trend Spotter',
    goal='Identify current market trends and emerging technologies',
    backstory='Tech journalist turned market analyst, Marcus has a finger on the pulse of the startup world. He excels at identifying upcoming trends and assessing their potential impact.',
    tools=[search_tool, duck_tool],
    llm=llm
)

olivia_pitchperfector = Agent(
    role='Pitch Perfector',
    goal='Analyze and improve pitch strategies',
    backstory='Startup pitch coach with a track record of helping founders secure funding. Olivia has a talent for crafting compelling narratives and identifying key selling points.',
    tools=[search_tool],
    llm=llm
)

ryan_companalyst = Agent(
    role='Competitive Analyst',
    goal='Conduct competitive analysis and market positioning',
    backstory='Former strategy consultant specializing in startup ecosystems. Ryan excels at mapping out competitive landscapes and identifying unique value propositions.',
    tools=[search_tool, scrape_tool],
    llm=llm
)

emily_techevaluator = Agent(
    role='Tech Evaluator',
    goal='Assess technical feasibility and innovation of ideas',
    backstory='Software engineer with experience in multiple startups. Emily has a broad understanding of various technologies and can evaluate the technical merit of startup ideas.',
    tools=[search_tool],
    llm=llm
)

david_synthesisguru = Agent(
    role='Synthesis Guru',
    goal='Synthesize information and generate final evaluation report',
    backstory='Experienced business writer and analyst, David has a talent for integrating diverse information into coherent, actionable reports. He ensures all aspects of the evaluation are considered and well-presented.',
    tools=[search_tool],
    llm=llm
)

# In-memory storage for simplicity
evaluation_jobs = {}

agents = [
    {"name": "Alex DataMiner", "role": "Data Miner"},
    {"name": "Samantha YCInsider", "role": "YC Insider"},
    {"name": "Marcus TrendSpotter", "role": "Trend Spotter"},
    {"name": "Olivia PitchPerfector", "role": "Pitch Perfector"},
    {"name": "Ryan CompAnalyst", "role": "Competitive Analyst"},
    {"name": "Emily TechEvaluator", "role": "Tech Evaluator"},
    {"name": "David SynthesisGuru", "role": "Synthesis Guru"}
]

workflow = [
    "Gather and analyze data on recent YC accepted applications",
    "Identify current YC selection criteria and preferences",
    "Analyze current market trends and emerging technologies",
    "Evaluate the given idea against YC criteria and market trends",
    "Assess technical feasibility and innovation of the idea",
    "Analyze and suggest improvements for the idea's pitch strategy",
    "Conduct competitive analysis and market positioning",
    "Synthesize all gathered information and generate final evaluation report"
]

# Step callback function
def step_callback(job_id, step_output):
    if isinstance(step_output, AgentFinish):
        status = "completed"
        result = step_output.return_values.get('output', '')
    else:
        status = "in_progress"
        result = str(step_output)

    current_step = evaluation_jobs[job_id].get('current_step', 0)
    current_agent = get_agent_for_step(current_step)

    evaluation_jobs[job_id]['current_step'] = current_step
    evaluation_jobs[job_id]['current_agent'] = current_agent
    evaluation_jobs[job_id]['tasks'][current_step - 1]['status'] = status
    evaluation_jobs[job_id]['tasks'][current_step - 1]['result'] = result

    socketio.emit('evaluation_update', {
        'job_id': job_id,
        'status': status,
        'result': result,
        'current_step': current_step,
        'total_steps': len(workflow),
        'step_description': workflow[current_step - 1],
        'current_agent': current_agent
    })

# Create tasks
def create_tasks(job_id):
    return [
        Task(
            description="Gather and analyze data on recent YC accepted applications",
            agent=alex_dataminer,
            expected_output="JSON document containing detailed information on recent YC accepted startups, including industry, funding, team composition, and key metrics",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Identify current YC selection criteria and preferences",
            agent=samantha_ycinsider,
            expected_output="Report outlining YC's current selection criteria, preferences, and any recent shifts in investment focus",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Analyze current market trends and emerging technologies",
            agent=marcus_trendspotter,
            expected_output="List of top market trends and emerging technologies relevant to YC's interests, with supporting data",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Evaluate the given idea against YC criteria and market trends",
            agent=ryan_companalyst,
            expected_output="Initial assessment report comparing the given idea to YC criteria and current market trends",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Assess technical feasibility and innovation of the idea",
            agent=emily_techevaluator,
            expected_output="Technical evaluation report detailing the idea's feasibility, innovativeness, and potential technical challenges",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Analyze and suggest improvements for the idea's pitch strategy",
            agent=olivia_pitchperfector,
            expected_output="Pitch analysis report with specific recommendations for improvement",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Conduct competitive analysis and market positioning",
            agent=ryan_companalyst,
            expected_output="Competitive landscape report and suggested market positioning strategy",
            callback=lambda output: step_callback(job_id, output)
        ),
        Task(
            description="Synthesize all gathered information and generate final evaluation report",
            agent=david_synthesisguru,
            expected_output="Comprehensive evaluation report assessing the idea's chances of YC acceptance, including strengths, weaknesses, and recommendations",
            callback=lambda output: step_callback(job_id, output)
        )
    ]

def get_agent_for_step(step):
    step_agent_map = {
        1: "Alex DataMiner",
        2: "Samantha YCInsider",
        3: "Marcus TrendSpotter",
        4: "Ryan CompAnalyst",
        5: "Emily TechEvaluator",
        6: "Olivia PitchPerfector",
        7: "Ryan CompAnalyst",
        8: "David SynthesisGuru"
    }
    return step_agent_map.get(step, "Unknown Agent")

def run_task(job_id, task_index):
    task = evaluation_jobs[job_id]['tasks_object'][task_index]
    crew = Crew(
        agents=[alex_dataminer, samantha_ycinsider, marcus_trendspotter, olivia_pitchperfector,
                ryan_companalyst, emily_techevaluator, david_synthesisguru],
        tasks=[task],
        process=Process.sequential
    )
    result = str(crew.kickoff())
    evaluation_jobs[job_id]['current_step'] = task_index + 1
    evaluation_jobs[job_id]['tasks'][task_index]['status'] = 'completed'
    evaluation_jobs[job_id]['tasks'][task_index]['result'] = result
    return result

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/evaluate', methods=['POST'])
def start_evaluation():
    idea = request.json['idea']
    job_id = str(uuid.uuid4())
    tasks = create_tasks(job_id)
    evaluation_jobs[job_id] = {
        'status': 'pending',
        'idea': idea,
        'current_step': 0,
        'tasks': [{'status': 'pending', 'result': None} for _ in tasks],
        'tasks_object': tasks,
    }
    return jsonify({'job_id': job_id}), 202

@app.route('/api/evaluate/<job_id>/status', methods=['GET'])
def get_evaluation_status(job_id):
    job = evaluation_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({
        'status': job['status'],
        'current_step': job.get('current_step', 0),
        'total_steps': len(workflow),
        'current_agent': job.get('current_agent'),
        'tasks': job['tasks']
    })

@app.route('/api/evaluate/<job_id>/task/<int:task_index>', methods=['POST'])
def execute_task(job_id, task_index):
    job = evaluation_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if task_index < 0 or task_index >= len(job['tasks']):
        return jsonify({'error': 'Invalid task index'}), 400
    if job['tasks'][task_index]['status'] == 'completed':
        return jsonify({'error': 'Task already completed'}), 400

    Thread(target=run_task, args=(job_id, task_index)).start()
    return jsonify({'message': 'Task execution started'}), 202

@app.route('/api/evaluate/<job_id>/results', methods=['GET'])
def get_evaluation_results(job_id):
    job = evaluation_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({'results': job['tasks']})

@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify(agents)

@app.route('/api/workflow', methods=['GET'])
def get_workflow():
    return jsonify(workflow)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=7457, debug=True)
