import os

from .code_map import load_code_folder_to_system_prompt
from .llm import query_llm
from .produce_files import produce_files
from .util import load_history, save_history


def refactor_frontend():
    print("Refactoring frontend into modular files", flush=True)
    
    # Load the current state of the project
    system_prompt = load_code_folder_to_system_prompt('.')
    
    query = '''Try to refactor the "index.html", break into smaller, modular ".css", ".js", ".html" files.
Each file is better to be less than 100 lines.

Use semantic naming for the new files.
Update the main HTML file to properly link the new CSS and JS files.
Output each new file content in the format <filename_extension>content</filename_extension>.'''
    
    responses, histories = query_llm(
        query,
        system_message=system_prompt,
        previous_history=load_history(prefix="refactor"),
        filename="frontend_refactor"
    )
    save_history(histories[0], prefix="refactor")
    produce_files(responses[0])


def refactor_backend():
    print("Refactoring backend into modular files", flush=True)
    
    # Load the current state of the project
    system_prompt = load_code_folder_to_system_prompt('.')
    
    query = '''Try to refactor the "server.py", break into smaller, modular ".py" files.
Each file is better to be less than 100 lines.
Also make "server.py" to be able to serve ".js" and ".css" files.

Use semantic naming for the new files.
Update the main server file to properly import and use the new modules.
Output each new file content in the format <filename_extension>content</filename_extension>.'''
    
    responses, histories = query_llm(
        query,
        system_message=system_prompt,
        previous_history=load_history(prefix="refactor"),
        filename="backend_refactor"
    )
    save_history(histories[0], prefix="refactor")
    produce_files(responses[0])


def refactor():
    refactor_frontend()
    refactor_backend()
