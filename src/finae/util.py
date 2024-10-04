import os
import pickle
from pathlib import Path
from typing import List

from .llm import ChatMessage


def assert_file_exists_and_read(filename):
    # Assert that the file exists
    assert os.path.exists(filename), f"File '{filename}' does not exist"

    # Read the file content
    try:
        with open(filename, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        assert False, f"Failed to read file '{filename}': {str(e)}"


def save_history(history, prefix='default'):
    history_filename = Path(f'{prefix}.history.pickle')
    with open(history_filename, 'wb') as f:
        return pickle.dump(history, f)


def load_history(prefix='default') -> List[ChatMessage]:
    history_filename = Path(f'{prefix}.history.pickle')
    if history_filename.exists():
        return pickle.loads(history_filename.read_bytes())
    return []


_PRODUCE_FILE_MAPPING = {
    'AGENTS_DESIGN': 'agents_design.json',
    'TASKS_DESIGN': 'tasks_design.json',
    'SERVER_PYTHON_CODE': 'server.py',
    'INDEX_HTML_CODE': 'index.html',
    'RUN_BASH_CODE': 'run.sh',
    'BACKEND_DESIGN': 'backend_design.txt',
    'FRONTEND_DESIGN': 'frontend_design.txt',
    'AGENTS_PYTHON_CODE': 'agents.py',
}


def parse_block(block_name, response_text):
    if f'<{block_name}>' in response_text:
        try:
            block_content = response_text.split(f'<{block_name}>')[
                1].split(f'</{block_name}>')[0]
            return block_content
        except:
            pass
    return None


def produce_files(response_text):
    for block_name, filename in _PRODUCE_FILE_MAPPING.items():
        block_content = parse_block(block_name, response_text)
        if block_content is not None:
            with open(filename, 'w') as f:
                f.write(block_content)
