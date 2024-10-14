import os

from .code_map import load_code_folder_to_system_prompt
from .llm import query_llm
from .util import load_history, save_history

def refactor_frontend():
    print("Refactoring frontend into modular files", flush=True)
    
    # Load the current state of the project
    system_prompt = load_code_folder_to_system_prompt('.')
    
    query = '''Refactor the "index.html" file into smaller, modular files (.css, .js, .html).
    Each file should be no more than 100 lines.
    Use semantic naming for the new files.
    Update the main HTML file to properly link the new CSS and JS files.
    Output each new file content in the format <filename_extension>content</filename_extension>.'''
    
    responses, histories = query_llm(
        query,
        system_message=system_prompt,
        previous_history=load_history(),
        filename="frontend_refactor"
    )
    save_history(histories[0])
    produce_files(responses[0])


def refactor_backend():
    print("Refactoring backend into modular files", flush=True)
    
    # Load the current state of the project
    system_prompt = load_code_folder_to_system_prompt('.')
    
    query = '''Refactor the "server.py" file into smaller, modular files (.py).
    Each file should be no more than 100 lines.
    Use semantic naming for the new files.
    Update the main server file to properly import and use the new modules.
    Output each new file content in the format <filename_extension>content</filename_extension>.'''
    
    responses, histories = query_llm(
        query,
        system_message=system_prompt,
        previous_history=load_history(),
        filename="backend_refactor"
    )
    save_history(histories[0])
    produce_files(responses[0])

