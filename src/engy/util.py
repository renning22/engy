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
        with open(filename, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        assert False, f"Failed to read file '{filename}': {str(e)}"


def save_history(history, prefix="default"):
    history_filename = Path(f"{prefix}.history.pickle")
    with open(history_filename, "wb") as f:
        return pickle.dump(history, f)


def load_history(prefix="default") -> List[ChatMessage]:
    history_filename = Path(f"{prefix}.history.pickle")
    if history_filename.exists():
        return pickle.loads(history_filename.read_bytes())
    return []
