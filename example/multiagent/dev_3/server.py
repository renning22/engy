
import os
import uuid
from threading import Thread

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain.tools import DuckDuckGoSearchRun
from langchain_community.tools import tool

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up the language model
llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.2)

# Initialize tools
search_tool = DuckDuckGoSearchRun()

@tool
def scrape_website(url: str) -> str:
    """Scrape the content of a given website"""
    # Implement web scraping logic here
    return f"Scraped content from {url}"

# Create agents
data_harvester = Agent(
    role='Data Harvester',
    goal='Collect comprehensive data from various sources about competitors',
    backstory='Experienced web scraper and data collection specialist with a background in digital marketing.',
    tools=[search_tool, scrape_website],
    llm=llm
)

trend_spotter = Agent(
    role='Trend Spotter',
    goal='Analyze market trends and industry benchmarks',
    backstory='Former market research analyst with a keen eye for emerging patterns and industry shifts.',
    tools=[search_tool],
    llm=llm
)

competitor_profiler = Agent(
    role='Competitor Profiler',
    goal='Create detailed SWOT analyses and competitive benchmarks',
    backstory='Strategic consultant with years of experience in competitive intelligence.',
    tools=[search_tool],
    llm=llm
)

price_watcher = Agent(
    role='Price Watcher',
    goal='Monitor and analyze competitor pricing strategies',
    backstory='E-commerce specialist with expertise in pricing analytics.',
    tools=[search_tool, scrape_website],
    llm=llm
)

insight_synthesizer = Agent(
    role='Insight Synthesizer',
    goal='Generate actionable insights and unique selling points',
    backstory='Former product marketing manager with a talent for distilling complex information into clear, actionable strategies.',
    tools=[search_tool],
    llm=llm
)

report_crafter = Agent(
    role='Report Crafter',
    goal='Compile and format the final competitor analysis report',
    backstory='Experienced technical writer and data visualization expert.',
    tools=[search_tool],
    llm=llm
)

integration_master = Agent(
    role='Integration Master',
    goal='Ensure seamless data flow and tool integration',
    backstory='Systems integration specialist with a background in marketing technology.',
    tools=[search_tool],
    llm=llm
)

# In-memory storage for simplicity
analysis_jobs = {}

agents = [
    {"name": "DataHarvester", "role": "Data Harvester"},
    {"name": "TrendSpotter", "role": "Trend Spotter"},
    {"name": "CompetitorProfiler", "role": "Competitor Profiler"},
    {"name": "PriceWatcher", "role": "Price Watcher"},
    {"name": "InsightSynthesizer", "role": "Insight Synthesizer"},
    {"name": "ReportCrafter", "role": "Report Crafter"},
    {"name": "IntegrationMaster", "role": "Integration Master"}
]

workflow = [
    "Collect comprehensive data about competitors from various sources",
    "Analyze market trends and industry benchmarks",
    "Create SWOT analyses and competitive benchmarks",
    "Analyze competitor pricing strategies",
    "Generate actionable insights and unique selling points",
    "Compile and format the final competitor analysis report",
    "Review and refine the compiled report",
    "Finalize report and prepare data for export"
]

def create_tasks(job_id, competitors):
    return [
        Task(
            description=f"Collect comprehensive data about competitors: {', '.join(competitors)}",
            agent=data_harvester,
            expected_output="Raw data in JSON format, including website content, social media data, news articles, press releases, and customer reviews",
        ),
        Task(
            description="Analyze market trends and industry benchmarks",
            agent=trend_spotter,
            expected_output="JSON document containing identified market trends, industry benchmarks, and visualizations of key patterns",
        ),
        Task(
            description="Create SWOT analyses and competitive benchmarks",
            agent=competitor_profiler,
            expected_output="JSON document with detailed SWOT analyses for each competitor and comparative benchmarks of key performance indicators",
        ),
        Task(
            description="Analyze competitor pricing strategies",
            agent=price_watcher,
            expected_output="JSON document containing price comparisons across different platforms, identified pricing patterns, and potential pricing strategies",
        ),
        Task(
            description="Generate actionable insights and unique selling points",
            agent=insight_synthesizer,
            expected_output="List of actionable insights and unique selling points for each competitor in JSON format",
        ),
        Task(
            description="Compile and format the final competitor analysis report",
            agent=report_crafter,
            expected_output="Draft of the comprehensive competitor analysis report in a structured document format (e.g., markdown or HTML)",
        ),
        Task(
            description="Review and refine the compiled report",
            agent=insight_synthesizer,
            expected_output="Refined and polished competitor analysis report with enhanced insights and narratives",
        ),
        Task(
            description="Finalize report and prepare data for export",
            agent=integration_master,
            expected_output="Final competitor analysis report in multiple formats (PDF, HTML, etc.) and structured data ready for export to other tools",
        )
    ]


def task_callback(task_output, task_index, job_id):
    analysis_jobs[job_id]['current_task'] = task_index
    analysis_jobs[job_id]['tasks'][task_index]['status'] = 'completed'
    analysis_jobs[job_id]['tasks'][task_index]['result'] = task_output
    socketio.emit('task_update', {
        'job_id': job_id,
        'task_index': task_index,
        'status': 'completed',
        'result': task_output
    })


def run_analysis(job_id, competitors):
    tasks = create_tasks(job_id, competitors)
    analysis_jobs[job_id]['tasks'] = [{'status': 'pending', 'result': None} for _ in tasks]
    
    crew = Crew(
        agents=[data_harvester, trend_spotter, competitor_profiler, price_watcher,
                insight_synthesizer, report_crafter, integration_master],
        tasks=tasks,
        process=Process.sequential
    )

    for i, task in enumerate(tasks):
        analysis_jobs[job_id]['current_task'] = i
        analysis_jobs[job_id]['tasks'][i]['status'] = 'in_progress'
        socketio.emit('task_update', {
            'job_id': job_id,
            'task_index': i,
            'status': 'in_progress'
        })
        
        result = str(crew.kickoff())
        task_callback(result, i, job_id)

    analysis_jobs[job_id]['status'] = 'completed'
    socketio.emit('analysis_update', {
        'job_id': job_id,
        'status': 'completed'
    })

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    competitors = request.json['competitors']
    job_id = str(uuid.uuid4())
    analysis_jobs[job_id] = {
        'status': 'in_progress',
        'competitors': competitors,
        'current_task': 0,
        'tasks': []
    }
    Thread(target=run_analysis, args=(job_id, competitors)).start()
    return jsonify({'job_id': job_id}), 202

@app.route('/api/analyze/<job_id>/status', methods=['GET'])
def get_analysis_status(job_id):
    job = analysis_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify(agents)

@app.route('/api/workflow', methods=['GET'])
def get_workflow():
    return jsonify(workflow)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=8922, debug=True)
