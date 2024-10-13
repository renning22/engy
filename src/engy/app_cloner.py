import os
import random
import shutil
from pathlib import Path

from .llm import auto_load_dotenv, query_llm
from .produce_files import produce_files
from .util import assert_file_exists_and_read, load_history, save_history

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


def load_example(path):
    file_contents = {}
    file_types = ['.py', '.html', '.css', '.js', '.sh']
    
    for file_path in Path(path).iterdir():
        if file_path.suffix in file_types:
            file_contents[file_path.name] = assert_file_exists_and_read(file_path)

    content = "# Example Project\n"
    content += "This is the example project which contains the following files:\n\n"

    for filename, file_content in file_contents.items():
        content += f"## {filename}\n"
        content += f"```{filename.split('.')[-1]}\n"
        content += file_content
        content += "\n```\n\n"

    content += "# Objective\n"
    content += "Modify and re-generate any of these files (if necessary) based on new <FEATURE_REQUEST></FEATURE_REQUEST> statements.\n\n"

    content += "# Output\n"
    content += "Output new or modified file contents using the following format:\n"
    content += "<filename_extension>File content goes here</filename_extension>\n"
    content += "For example:\n"
    content += "<myfile_py>print('Hello, World!')</myfile_py>\n"
    content += "This will create or update a file named 'myfile.py' with the given content.\n\n"
    content += "## Note\n"
    content += "1. Only output one file in each conversation round, based on the user query.\n"
    content += "2. Once a file is updated, already print the entire new content of the file.\n"
    content += "3. When no file is needed to update, output \"===end of generation===\".\n"

    return content


def clone_all(path, prompts):
    try:
        shutil.copy2(os.path.join(path, '.env'), '.env')
        auto_load_dotenv()
    except (FileNotFoundError, shutil.SameFileError, OSError):
        pass  # Silently ignore errors

    system_prompts = load_example(path)
    generate_backend(prompts, system_prompts)
    generate_frontend(system_prompts)
    generate_run_bash(system_prompts)
