import random

from .llm import query_llm
from .util import load_history, save_history, assert_file_exists_and_read, produce_files

PORT = random.randint(5000, 10000)


DESIGN_SYSTEM_PROMPT = f'''You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model, specialized in software development.
You are a software architecture.
Your job to design an app. The app is usually very simple and can be always expressed in a python web server backend plus a single html page frontend.
The given input is the app description.
Use your imagination to design a fancy app with only one python server (backend) with only one html page (frontend).
You only write the design doc with high-level structure and psudocode, no need to write actual code.  

The output backend design should be in <BACKEND_DESIGN></BACKEND_DESIGN> block.
The output frontend design should be in <FRONTEND_DESIGN></FRONTEND_DESIGN> block.
There should be exactly one <BACKEND_DESIGN> and one <FRONTEND_DESIGN>.
'''

SERVER_SYSTEM_PROMPT = f'''You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model, specialized in backend development.
You are good at writing python webserver in single self-contained python files.

1. Regarding data or database.
If provide API key and mention API to use, generate client to actually connect to the API. (assume API is accesible and key is correct.)
Otherwise, generate mock data and prefer to use in-memory data-structure database.
When use sqlite, use local file database (in current directory).

2. You may use libraries like Flask, websocket and etc.
When use Flask, also enable CORS.

3. Do not add authentication or login (or admin account). Make it public accessible and focus on application functionality.

4. Bind to `0.0.0.0:{PORT}`.

Output python source code should be included in <SERVER_PYTHON_CODE></SERVER_PYTHON_CODE> block.
'''

HTML_SYSTEM_PROMPT = f'''You are an expert in Web development, including CSS, JavaScript, React, Tailwind, Node.JS and Hugo / Markdown. You are expert at selecting and choosing the best tools, and doing your utmost to avoid unnecessary duplication and complexity.
When making a suggestion, you break things down in to discrete changes, and suggest a small test after each stage to make sure things are on the right track.
Produce code to illustrate examples, or when directed to in the conversation. If you can answer without code, that is preferred, and you will be asked to elaborate if it is required.
Before writing or suggesting code, you conduct a deep-dive review of the existing code and describe how it works between <CODE_REVIEW> tags. Once you have completed the review, you produce a careful plan for the change in <PLANNING> tags. Pay attention to variable names and string literals - when reproducing code make sure that these do not change unless necessary or directed. If naming something by convention surround in double colons and in ::UPPERCASE::.
Finally, you produce correct outputs that provide the right balance between solving the immediate problem and remaining generic and flexible.
You always ask for clarifications if anything is unclear or ambiguous. You stop to discuss trade-offs and implementation options if there are choices to make.
It is important that you follow this approach, and do your best to teach your interlocutor about making effective decisions. You avoid apologising unnecessarily, and review the conversation to never repeat earlier mistakes.
You are keenly aware of security, and make sure at every step that we don't do anything that could compromise data or introduce new vulnerabilities. Whenever there is a potential security risk (e.g. input handling, authentication management) you will do an additional review, showing your reasoning between <SECURITY_REVIEW> tags.
Finally, it is important that everything produced is operationally sound. We consider how to host, manage, monitor and maintain our solutions. You consider operational concerns at every step, and highlight them where they are relevant.
Bonus: if you can use 3djs or WebGL anywhere need a render or dashboard, use it.  

Assume the server is already running at `0.0.0.0:{PORT}`, generate html code that connects to the server.  

Final html code should be included in <INDEX_HTML_CODE></INDEX_HTML_CODE> block.
'''

BASH_SYSTEM_PROMPT = '''You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model, specialized in software development.
You are experts in python 3.11, and familier with popular libraries, and also good at writing linux bash scripts.

You are currently on a task to write "run.sh" that:
1. create a temp venv
2. use pip to install all the required libaries
3. use python to start the webserver. ("python server.py")

(Assume anaconda and pip are installed.)

Generated scripts should be included in <RUN_BASH_CODE></RUN_BASH_CODE> block.

E.g.
<RUN_BASH_CODE>
#!/bin/sh

# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

pip install Flask websocket

python server.py
</RUN_BASH_CODE>
'''


def generate_design(problem):
    print('Generate system design', flush=True)
    query = f'''# The problem to solve:
<PROBLEM>
{problem}
</PROBLEM>

Based on given app description, generate <BACKEND_DESIGN> and <FRONTEND_DESIGN>.
<BACKEND_DESIGN> will be written in "backend_design.txt".
<FRONTEND_DESIGN> will be written in "frontend_design.txt".
'''
    responses, histories = query_llm(
        query, system_message=DESIGN_SYSTEM_PROMPT, filename='design')
    save_history(histories[0])
    produce_files(responses[0])


def generate_backend():
    backend_design_prompts = assert_file_exists_and_read('backend_design.txt')
    print('Generate server.py', flush=True)
    query = f'''Generate "server.py". Backend design:
```
{backend_design_prompts}
```
'''
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server.py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_frontend():
    frontend_design_prompts = assert_file_exists_and_read(
        'frontend_design.txt')
    print('Generate index.html', flush=True)
    query = f'''Generate "index.html" that connect to the server. The "index.html" design:
```
{frontend_design_prompts}
```
'''
    responses, histories = query_llm(
        query, system_message=HTML_SYSTEM_PROMPT, previous_history=load_history(), filename='index.html')
    save_history(histories[0])
    produce_files(responses[0])


def stylize_frontend():
    print('Stylize index.html', flush=True)
    query = f'''Stylize and make "index.html" beatuful, look production-ready, by using pure CSS website framework "Tailwind CSS".'''
    responses, histories = query_llm(
        query, system_message=HTML_SYSTEM_PROMPT, previous_history=load_history(), filename='index.html')
    save_history(histories[0])
    produce_files(responses[0])


def revise_backend():
    print('Modify server.py', flush=True)
    query = 'Modify "server.py" to also serve "index.html" like a static web server.'
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server.py')
    save_history(histories[0])
    produce_files(responses[0])


def generate_run_bash():
    print('Generate run.sh', flush=True)
    query = f'Generate "run.sh" to pip install required libraries and start the server.'
    responses, histories = query_llm(
        query, system_message=BASH_SYSTEM_PROMPT, previous_history=load_history(), filename='run.sh')
    save_history(histories[0])
    produce_files(responses[0])


def generate_all(problem):
    generate_design(problem)
    generate_backend()
    generate_frontend()
    stylize_frontend()
    revise_backend()
    generate_run_bash()


def regenerate_backend(prompts):
    print('Re-generate server.py', flush=True)
    query = f'{prompts}\n\nRegenerate "server.py".'
    responses, histories = query_llm(
        query, system_message=SERVER_SYSTEM_PROMPT, previous_history=load_history(), filename='server.py')
    save_history(histories[0])
    produce_files(responses[0])


def regenerate_frontend(prompts):
    print('Re-generate index.html', flush=True)
    query = f'{prompts}\n\nRegenerate "index.html".'
    responses, histories = query_llm(
        query, system_message=HTML_SYSTEM_PROMPT, previous_history=load_history(), filename='index.html')
    save_history(histories[0])
    produce_files(responses[0])


def regenerate_all(prompts):
    regenerate_backend(prompts)
    regenerate_frontend('According the changes to the server.')

