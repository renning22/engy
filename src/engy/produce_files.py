import re

_PRODUCE_FILE_MAPPING = {
    "AGENTS_DESIGN": "agents_design.json",
    "TASKS_DESIGN": "tasks_design.json",
    "SERVER_PYTHON_CODE": "server.py",
    "INDEX_HTML_CODE": "index.html",
    "RUN_BASH_CODE": "run.sh",
    "BACKEND_DESIGN": "backend_design.txt",
    "FRONTEND_DESIGN": "frontend_design.txt",
    "AGENTS_PYTHON_CODE": "agents.py",
    "DOCKERFILE": "Dockerfile",
    "RUN_DOCKER_BASH": "run_docker.sh",
    "SERVER_UNIT_TESTS_PYTHON_CODE": "server_test.py",
}


def parse_block(block_name, response_text):
    pattern = f"<{block_name}>(.*?)</{block_name}>"
    match = re.search(pattern, response_text, re.DOTALL)
    return match.group(1) if match else None


def produce_files(response_text):
    # First, process the predefined mappings
    for block_name, filename in _PRODUCE_FILE_MAPPING.items():
        block_content = parse_block(block_name, response_text)
        if block_content is not None:
            with open(filename, "w") as f:
                f.write(block_content)
            print(f"New file written: {filename}")

    # Then, look for any other blocks with the format <anyname_extension>
    pattern = r"<(\w+)_(\w+)>(.*?)</\1_\2>"
    matches = re.finditer(pattern, response_text, re.DOTALL)

    for match in matches:
        block_name = match.group(1)
        extension = match.group(2)
        content = match.group(3)

        # Check if this block name is not in the predefined mapping
        if f"{block_name.upper()}_{extension.upper()}" not in _PRODUCE_FILE_MAPPING:
            filename = f"{block_name}.{extension}"
            with open(filename, "w") as f:
                f.write(content)
            print(f"New file written: {filename}")

    print("Files have been produced based on the response text.")
