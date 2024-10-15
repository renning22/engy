from .code_map import load_code_folder_to_system_prompt
from .llm import query_llm
from .produce_files import produce_files
from .util import load_history, save_history


def split_frontend():
    print("Splitting frontend into modular files", flush=True)
    
    # Load the current state of the project
    system_prompt = load_code_folder_to_system_prompt('.')
    
    query = '''Split the "index.html" into smaller, modular ".css", ".js", ".html" files.
Each file should preferably be less than 100 lines.

Use semantic naming for the new files.
Update the main HTML file to properly link the new CSS and JS files.
Output each new file content in the format <filename_extension>content</filename_extension>.'''
    
    responses, histories = query_llm(
        query,
        system_message=system_prompt,
        previous_history=load_history(prefix="split"),
        filename="frontend_split"
    )
    save_history(histories[0], prefix="split")
    produce_files(responses[0])


def split_backend():
    print("Splitting backend into modular files", flush=True)
    
    # Load the current state of the project
    system_prompt = load_code_folder_to_system_prompt('.')
    
    query = '''Split the "server.py" into smaller, modular ".py" files.
Each file should preferably be less than 100 lines.
Also update "server.py" to be able to serve ".js" and ".css" files.

Use semantic naming for the new files.
Update the main server file to properly import and use the new modules.
Output each new file content in the format <filename_extension>content</filename_extension>.'''
    
    responses, histories = query_llm(
        query,
        system_message=system_prompt,
        previous_history=load_history(prefix="split"),
        filename="backend_split"
    )
    save_history(histories[0], prefix="split")
    produce_files(responses[0])


def split():
    split_frontend()
    split_backend()
