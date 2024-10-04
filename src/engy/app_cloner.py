import os
import random
import shutil

from .llm import query_llm
from .util import load_history, save_history, assert_file_exists_and_read, produce_files


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
    server_py = assert_file_exists_and_read(os.path.join(path, 'server.py'))
    index_html = assert_file_exists_and_read(os.path.join(path, 'index.html'))
    run_sh = assert_file_exists_and_read(os.path.join(path, 'run.sh'))

    return f'''# Example Project
This is the example project which has 3 main files "server.py", "index.html" and "run.sh".
Here are their contents:

## server.py
```python
{server_py}
```

## index.html
```html
{index_html}
```

## run.sh
```bash
{run_sh}
```

# Objective
Modify and re-generate these files based on new <FEATURE_REQUEST></FEATURE_REQUEST> statements.

# Output
1. Output new "server.py" source code in <SERVER_PYTHON_CODE></SERVER_PYTHON_CODE> block.
2. Output new "index.html" source code in <INDEX_HTML_CODE></INDEX_HTML_CODE> block.
3. Output new "run.sh" source code in <RUN_BASH_CODE></RUN_BASH_CODE> block.

Only output one of them in each conversation round, based on user query.
'''


def clone_all(path, prompts):
    try:
        shutil.copy2(os.path.join(path, '.env'), '.env')
    except (FileNotFoundError, shutil.SameFileError, OSError):
        pass  # Silently ignore errors

    system_prompts = load_example(path)
    generate_backend(prompts, system_prompts)
    generate_frontend(system_prompts)
    generate_run_bash(system_prompts)
