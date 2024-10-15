"""Read all code files in current folder and turn into prompts."""

from pathlib import Path

from .util import assert_file_exists_and_read

def load_code_folder_to_system_prompt(path):
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
    content += "2. Once a file is updated, always print the full content (no diff format).\n"
    content += "3. When no file is to update, output \"===end of generation===\".\n"

    return content
