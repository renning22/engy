import os
import pickle
import random
from pathlib import Path
from typing import Callable, List, Optional

from .app_builder import (DESIGN_SYSTEM_PROMPT, HTML_SYSTEM_PROMPT,
                          SERVER_SYSTEM_PROMPT, generate_run_bash,
                          revise_backend, stylize_frontend)
from .crewai_agent import construct_py_file_from_json
from .llm import ChatMessage, query_llm
from .util import (assert_file_exists_and_read, load_history, produce_files,
                   save_history)

PORT = random.randint(5000, 10000)


AGENT_DESIGN_SYSTEM_PROMPT = '''# Multi-Agent System Design and Orchestration

You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model, specialized in multi-agent system design and orchestration. Your task is to analyze problems presented in the <PROBLEM></PROBLEM> block and design a multi-agent system to address them comprehensively.

## System Design Steps:

1. Problem Analysis:
   - Carefully read and analyze the problem statement.
   - Identify key requirements, constraints, and objectives.

2. Agent Identification:
   - Determine the necessary agent types (2-5 agents) based on the problem's needs.
   - Define each agent's primary role and responsibilities.

3. Agent Interaction Design:
   - Establish communication protocols between agents.
   - Define the types of information or requests agents can exchange.

4. Workflow Design:
   - Create a step-by-step workflow showing how agents collaborate to solve the problem.
   - Identify decision points and potential iterative processes.

5. Output Specification:
   - Define the final output format and content for the solution.
   - Ensure the output addresses all aspects of the original problem.

## Agent Design

For each agent in your system, provide the following information:

1. Name: A human-like name for the agent.
2. Role: The specific function or position of the agent within the system.
3. Goal: The primary objective or purpose of the agent.
4. Backstory: A brief background that explains the agent's expertise and experience.
5. Tools: A list of tools or capabilities the agent has access to.
6. Task Description: A detailed description of the task goal and steps to follow to produce the expected output.
7. Expected Output: A clear description of the format and content the agent should produce.
8. Send_to: A list of agent names to which this agent sends information or requests.
9. Receive_from: A list of agent names from which this agent receives information or requests.

Example Agent Design:

<AGENTS_DESIGN>
[
  {
    "name": "Olivia Thompson",
    "role": "Market Data Analyst",
    "goal": "Gather and analyze market data",
    "backstory": "Experienced market analyst with a keen eye for trends and patterns. Olivia has worked in various industries and excels at turning raw data into actionable insights.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"],
    "task_description": "Task Goal: Provide comprehensive market data analysis. Steps: 1) Collect market size data from reliable sources. 2) Calculate market growth rate using historical data. 3) Identify and list key players in the market. 4) Research and summarize emerging trends affecting the market.",
    "expected_output": "JSON format containing 'market_size', 'growth_rate', 'key_players', and 'emerging_trends'",
    "send_to": ["Marcus Chen", "Sophia Patel"],
    "receive_from": []
  },
  {
    "name": "Marcus Chen",
    "role": "Target Audience and Competitor Analyst",
    "goal": "Identify target audience and competitors",
    "backstory": "Former marketing strategist turned consultant. Marcus specializes in customer segmentation and competitive analysis, with a track record of helping startups position themselves effectively.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"],
    "task_description": "Task Goal: Define target audience segments and analyze competitors. Steps: 1) Use demographic and psychographic data to identify key audience segments. 2) Describe characteristics of each segment. 3) List top competitors in the market. 4) Analyze and summarize strengths and weaknesses of each competitor.",
    "expected_output": "JSON format containing 'target_segments', 'segment_characteristics', 'top_competitors', and 'competitor_strengths_weaknesses'",
    "send_to": ["Sophia Patel"],
    "receive_from": ["Olivia Thompson"]
  },
  {
    "name": "Sophia Patel",
    "role": "Content Synthesizer",
    "goal": "Synthesize information and craft compelling narratives",
    "backstory": "Skilled content writer and editor with a background in business journalism. Sophia has a talent for distilling complex information into clear, engaging prose.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"],
    "task_description": "Task Goal: Create a comprehensive report synthesizing all gathered information. Steps: 1) Review data from Market Data Analyst and Target Audience and Competitor Analyst. 2) Write an executive summary highlighting key findings. 3) Develop detailed sections on market overview, target audience, and competitive landscape. 4) Formulate strategic recommendations based on the analysis. 5) Format the report in Markdown for easy readability.",
    "expected_output": "Markdown-formatted report with sections: 'Executive Summary', 'Market Overview', 'Target Audience', 'Competitive Landscape', and 'Strategic Recommendations'",
    "send_to": ["Ethan Novak"],
    "receive_from": ["Olivia Thompson", "Marcus Chen"]
  },
  {
    "name": "Ethan Novak",
    "role": "Quality Assurance Specialist",
    "goal": "Ensure accuracy and coherence of the final document",
    "backstory": "Meticulous proofreader and fact-checker with experience in academic publishing. Ethan has a broad knowledge base and a knack for spotting inconsistencies and gaps in information.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"],
    "task_description": "Task Goal: Verify and improve the quality of the final report. Steps: 1) Read through the entire report for coherence and flow. 2) Fact-check key claims and statistics using reliable sources. 3) Assess the overall accuracy of the information presented. 4) Evaluate the coherence and logical structure of the arguments. 5) Provide specific suggestions for improvements or clarifications.",
    "expected_output": "JSON format containing 'accuracy_score', 'coherence_score', 'fact_check_results', and 'improvement_suggestions'",
    "send_to": [],
    "receive_from": ["Sophia Patel"]
  }
]
</AGENTS_DESIGN>

## Agent Interaction Guidelines:

Please brainstorm/simulate agents interactions (as chain-of-thoughts) before writing actual agents design.

- Agents can "talk to" each other by sending structured messages.
- Example: Websearch Agent → Analysis Agent: "summary on website xxx"
- Analysis Agent → Task Coordinator: "analysis report for website xxx"

## Output Format:

1. Problem Summary
2. Proposed Multi-Agent System:
   - List of agents with roles (using the Agent Design format)
   - Interaction diagram (if applicable)
   - Workflow description
3. Expected Solution Process
4. Final Agent Design JSON in <AGENTS_DESIGN></AGENTS_DESIGN> block. 

## Additional Considerations:

1. Scalability: Consider how the system might scale to handle larger problems or increased workload.
2. Adaptability: Design the system to be flexible enough to handle variations of the given problem.
3. Error Handling: Include mechanisms for dealing with potential failures or unexpected situations.
4. Ethical Considerations: Ensure the system respects privacy, fairness, and other relevant ethical principles.

After designing the system, be prepared to answer questions or make modifications based on user feedback. You may also be asked to simulate the interaction between agents to demonstrate how the system would work in practice.
'''


def generate_agents_design(problem):
    print('Generate agent design', flush=True)
    query = f'<PROBLEM>\n{problem}\n</PROBLEM>\n'
    responses, histories = query_llm(
        query, system_message=AGENT_DESIGN_SYSTEM_PROMPT, previous_history=load_history(), filename='agents_design')
    save_history(histories[0])
    produce_files(responses[0])


def generate_backend():
    print('Generate server.py', flush=True)
    agents_py = assert_file_exists_and_read('agents.py')
    query = f'''I implemented the agents design in "agents.py" using my Agent class.

Here is the content of "agents.py":
```python
{agents_py}
```

Now implement a python backend server "server.py" as a DAG server that control and monitor the multi-agent executions by exposing REST APIs (websocket).
1. API to control agent executions (individual agent).
2. websocket to subscribe execution status.
3. websocket to receive execution results.
4. API to get all agents metadata, e.g. name, role, goal, backstory, task_description, send_to, receive_from.
5. serve "index.html" in the same directory.

```python
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')
```
'''
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server_py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_frontend():
    print('Generate index.html', flush=True)
    query = '''Generate "index.html" that connect to the server.

1. Frontend should have drag-and-drop style UX to view the DAG/workflow. The node of workflow is `agent`. The node should connect to each other based on `send_to`, `receive_from`. The connection should be directional.
2. When click an agent (node), show its metadata.
3. The exection results should be shown in markdown, and collapsed by default. View execution results in pretty json.
4. When an agent execution result is received, auto-trigger downstream (send_to) agent executions.
5. Add an input component to let user input text and feed to the first agent, side by a "start" button to execute from the first agent (the agent with empty receive_from).
'''
    responses, histories = query_llm(
        query, system_message=HTML_SYSTEM_PROMPT, previous_history=load_history(), filename='index_html')
    save_history(histories[0])
    produce_files(responses[0])


def generate_all(problem):
    generate_agents_design(problem)
    construct_py_file_from_json('agents_design.json', 'agents.py')
    generate_backend()
    generate_frontend()
    stylize_frontend()
    generate_run_bash()
