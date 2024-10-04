import os
import pickle
import random
from pathlib import Path
from typing import Callable, List, Optional

from .app_builder import (DESIGN_SYSTEM_PROMPT, HTML_SYSTEM_PROMPT,
                          SERVER_SYSTEM_PROMPT, generate_run_bash,
                          revise_backend, stylize_frontend)
from .llm import ChatMessage, query_llm
from .multi_agent_builder import generate_agents_design
from .util import load_history, produce_files, save_history

PORT = random.randint(5000, 10000)


def read_code_example():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    example_file_path = os.path.join(
        current_dir, 'example', 'multiagent_server_1.py')
    with open(example_file_path, 'r') as file:
        return file.read()


def generate_backend():
    print('Generate server.py', flush=True)
    query = f'''Implement the agents/tasks design based on modifying this code example.

<code_example>
{read_code_example()}
</code_example>
'''
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server_py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_frontend():
    print('Generate index.html', flush=True)
    query = '''Generate "index.html" that connect to the server.

Frontend should have UX component to refect each agents, the overall workflow, the execution status of the workflow and results.   
'''
    responses, histories = query_llm(
        query, system_message=HTML_SYSTEM_PROMPT, previous_history=load_history(), filename='index_html')
    save_history(histories[0])
    produce_files(responses[0])


def generate_all(problem):
    generate_agents_design(problem)
    generate_backend()
    generate_frontend()
    stylize_frontend()
    generate_run_bash()
