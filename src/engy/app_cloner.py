import os
import random
import shutil

from .code_map import load_code_folder_to_system_prompt
from .llm import auto_load_dotenv, query_llm
from .produce_files import produce_files
from .util import load_history, save_history

PORT = random.randint(5000, 10000)


def generate_backend(prompts, system_prompts):
    print('Generate server.py', flush=True)
    query = f'''<FEATURE_REQUEST>
{prompts}
</FEATURE_REQUEST>

Generate new "server.py" first. Re-assign a new PORT, to "0.0.0.0:{PORT}".
'''
    responses, histories = query_llm(
        query, system_message=system_prompts, previous_history=load_history(), filename='server.py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_frontend(system_prompts):
    print('Generate index.html', flush=True)
    query = 'Generate new "index.html"'
    responses, histories = query_llm(
        query, system_message=system_prompts, previous_history=load_history(), filename='index.html')
    save_history(histories[0])
    produce_files(responses[0])


def generate_run_bash(system_prompts):
    print('Generate run.sh', flush=True)
    query = 'Generate new "run.sh". Only add new missing install, no need to make big changes.'
    responses, histories = query_llm(
        query, system_message=system_prompts, previous_history=load_history(), filename='run.sh')
    save_history(histories[0])
    produce_files(responses[0])


def clone_all(path, prompts):
    try:
        shutil.copy2(os.path.join(path, '.env'), '.env')
        auto_load_dotenv()
    except (FileNotFoundError, shutil.SameFileError, OSError):
        pass  # Silently ignore errors

    system_prompts = load_code_folder_to_system_prompt(path)
    generate_backend(prompts, system_prompts)
    generate_frontend(system_prompts)
    generate_run_bash(system_prompts)
