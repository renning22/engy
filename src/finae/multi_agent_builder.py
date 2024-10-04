import os
import pickle
import random
from pathlib import Path
from typing import Callable, List, Optional

from .app_builder import (DESIGN_SYSTEM_PROMPT, HTML_SYSTEM_PROMPT,
                          SERVER_SYSTEM_PROMPT, generate_run_bash,
                          revise_backend, stylize_frontend)
from .example.crew_ai import crew_ai_code_example
from .llm import query_llm
from .util import load_history, produce_files, save_history

PORT = random.randint(5000, 10000)


AGENT_DESIGN_SYSTEM_PROMPT = f'''You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model, specialized in multi-agent system design and orchestration.

Your task is to analyze the problem presented in the <PROBLEM></PROBLEM> block and design a multi-agent system to address it comprehensively. Follow these steps:

1. Problem Analysis:
   - Carefully examine the problem statement.
   - Identify key components, constraints, and objectives.
   - Break down the problem into subtasks or areas of expertise.

2. Agent Design:
   - Create a roster of 3-7 specialized agents to tackle different aspects of the problem.
   - For each agent, define:
     a. Role/Title
     b. Primary responsibilities
     c. Key skills or knowledge areas
     d. Input requirements
     e. Expected outputs
     f. Tools to be used 

3. System Architecture:
   - Outline how the agents will interact and collaborate.
   - Determine the flow of information and tasks between agents.
   - Identify any central coordination mechanism or hierarchy if needed.

4. Workflow Description:
   - Provide a step-by-step description of how the multi-agent system will process the problem.
   - Explain how inputs are handled, how intermediate results are shared, and how the final solution is produced.

5. Error Handling and Edge Cases:
   - Consider potential failure points or challenging scenarios.
   - Describe how the system will handle unexpected inputs or conflicts between agents.

6. Evaluation and Iteration:
   - Propose methods to assess the effectiveness of the multi-agent system.
   - Suggest ways to refine and improve the system based on performance.

Present your multi-agent system design in a clear, structured format. Use your knowledge and creativity to develop a solution that leverages the strengths of multiple specialized agents working in concert.

If any part of the problem or requirements is unclear, ask for clarification before proceeding with the design.
'''


AGENT_CODER_SYSTEM_PROMPT = f'''You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model, specialized in LLM agent python development.
You are good at using CrewAI library to code multi-agent workflow.

Some CrewAI library sample code:
```python
{crew_ai_code_example}
```

Output python source code should be included in <AGENTS_PYTHON_CODE></AGENTS_PYTHON_CODE> block.
'''


def generate_agents_design(problem):
    print('Generate agent design', flush=True)
    query = f'<PROBLEM>\n{problem}\n</PROBLEM>\n' + '''
Design a list of agents, output in JSON format and put in <AGENTS_DESIGN></AGENTS_DESIGN> block.
(content in <AGENTS_DESIGN> will create file and written to "agents_design.json")

E.g.
```
<AGENTS_DESIGN>
[
  {
    "name": "Olivia Thompson",
    "goal": "Gather and analyze market data",
    "backstory": "Experienced market analyst with a keen eye for trends and patterns. Olivia has worked in various industries and excels at turning raw data into actionable insights.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"]
  },
  {
    "name": "Marcus Chen",
    "goal": "Identify target audience and competitors",
    "backstory": "Former marketing strategist turned consultant. Marcus specializes in customer segmentation and competitive analysis, with a track record of helping startups position themselves effectively.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"]
  },
  {
    "name": "Sophia Patel",
    "goal": "Synthesize information and craft compelling narratives",
    "backstory": "Skilled content writer and editor with a background in business journalism. Sophia has a talent for distilling complex information into clear, engaging prose.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"]
  },
  {
    "name": "Ethan Novak",
    "goal": "Ensure accuracy and coherence of the final document",
    "backstory": "Meticulous proofreader and fact-checker with experience in academic publishing. Ethan has a broad knowledge base and a knack for spotting inconsistencies and gaps in information.",
    "tools": ["search_tool", "scrape_tool", "duckduck_tool"]
  }
]
</AGENTS_DESIGN>
```
'''
    responses, histories = query_llm(
        query, system_message=AGENT_DESIGN_SYSTEM_PROMPT, previous_history=load_history(), filename='tasks_design')
    save_history(histories[0])
    produce_files(responses[0])

    query = '''
Using these agents, think about a linear workflow to finish the task, each step has a "description", "agent" and "expected_output", the step output will be passing to the next step.
Output in JSON format and put in <TASKS_DESIGN></TASKS_DESIGN> block.
(content in <TASKS_DESIGN> will create file and written to "tasks_design.json")

E.g.
```
<TASKS_DESIGN>
[
  {
    "step": 1,
    "description": "Gather relevant market data and statistics",
    "expected_output": "Compiled market data in JSON format, including market size, growth rate, and key trends",
    "agent": "Olivia Thompson",
  },
  {
    "step": 2,
    "description": "Analyze target audience and identify main competitors",
    "expected_output": "JSON document containing target audience segments and a list of top competitors with their market shares",
    "agent": "Marcus Chen"
  },
  {
    "step": 3,
    "description": "Analyze gathered data and extract key insights",
    "expected_output": "List of key insights and their implications for the market",
    "agent": "Olivia Thompson"
  },
  {
    "step": 4,
    "description": "Create an outline for the 1-pager based on gathered information",
    "expected_output": "Detailed outline of the 1-pager in markdown format",
    "agent": "Sophia Patel"
  },
  {
    "step": 5,
    "description": "Write the first draft of the market research 1-pager",
    "expected_output": "First draft of the 1-pager in markdown format",
    "agent": "Sophia Patel"
  },
  {
    "step": 6,
    "description": "Review and fact-check the first draft",
    "expected_output": "Reviewed document with suggestions for improvements and corrections",
    "agent": "Ethan Novak"
  },
  {
    "step": 7,
    "description": "Incorporate feedback and finalize the 1-pager",
    "expected_output": "Final version of the market research 1-pager in markdown format",
    "agent": "Sophia Patel"
  },
  {
    "step": 8,
    "description": "Perform final proofreading and quality check",
    "expected_output": "Proofread and approved market research 1-pager, ready for presentation",
    "agent": "Ethan Novak"
  }
]
</TASKS_DESIGN>
```
'''
    print('Generate task design', flush=True)
    responses, histories = query_llm(
        query, system_message=AGENT_DESIGN_SYSTEM_PROMPT, previous_history=load_history(), filename='tasks_design')
    save_history(histories[0])
    produce_files(responses[0])


def generate_agent_py():
    query = 'Based on "agents_design.json" and "tasks_design.json", implement "agents.py"'
    print('Generate agents.py', flush=True)
    responses, histories = query_llm(
        query, system_message=AGENT_CODER_SYSTEM_PROMPT, previous_history=load_history(), filename='agents_py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_design():
    print('Generate system design', flush=True)
    query = '''Given the multi-agent design and implementation "agents.py", brainstorm backend/frontend system designs.

Backend should expose APIs to control the agents executions and reflect the status of execution, and results.
Frontend should have UX component to refect each agents, the overall workflow, the execution status of the workflow and results.   

generate <BACKEND_DESIGN> and <FRONTEND_DESIGN>.
'''
    responses, histories = query_llm(
        query, system_message=DESIGN_SYSTEM_PROMPT, previous_history=load_history(), filename='system_design')
    save_history(histories[0])
    produce_files(responses[0])


def generate_backend():
    print('Generate server.py', flush=True)
    query = '''Based on <BACKEND_DESIGN>, generate "server.py".
1. The python server should expose APIs to control the agents executions and reflect the status of execution, and results.
2. Serve "index.html" like a static web server.
3. Try not to use any task framework e.g. Celery.
'''
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server_py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_frontend():
    print('Generate index.html', flush=True)
    query = 'Based on <FRONTEND_DESIGN>, generate "index.html" that connect to the server.'
    responses, histories = query_llm(
        query, system_message=HTML_SYSTEM_PROMPT, previous_history=load_history(), filename='index_html')
    save_history(histories[0])
    produce_files(responses[0])


def revise_agents():
    print('Modify agents.py', flush=True)
    query = f'''Modify "agents.py", use step_callback to escalate step execution status (and intermidiate results) to server.'''
    responses, histories = query_llm(
        query, system_message=AGENT_CODER_SYSTEM_PROMPT, previous_history=load_history(), filename='agents_py')
    save_history(histories[0])
    produce_files(responses[0])


def revise_backend():
    print('Modify server.py', flush=True)
    query = 'Modify "server.py" to use and receive the step_callback information from "agents.py".'
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server.py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_all(problem):
    generate_agents_design(problem)
    generate_agent_py()
    generate_design()
    generate_backend()
    revise_agents()
    revise_backend()
    generate_frontend()
    stylize_frontend()
    generate_run_bash()
