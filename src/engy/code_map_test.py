import unittest
import tempfile
import os
from pathlib import Path
from textwrap import dedent

# Assuming the original function is in a file named 'code_loader.py'
from .code_map import load_code_folder_to_system_prompt

class TestLoadCodeFolderToSystemPrompt(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        # Create example files
        self.create_file('main.py', 'print("Hello, World!")')
        self.create_file('styles.css', 'body { color: blue; }')
        self.create_file('script.js', 'console.log("JavaScript");')
        self.create_file('index.html', '<h1>Hello</h1>')
        self.create_file('setup.sh', 'echo "Setup complete"')
        self.create_file('readme.txt', 'This file should be ignored')

    def create_file(self, filename, content):
        path = Path(self.temp_dir.name) / filename
        path.write_text(content)

    def test_load_code_folder_to_system_prompt(self):
        result = load_code_folder_to_system_prompt(self.temp_dir.name)

        # Check if all expected files are included
        self.assertIn('main.py', result)
        self.assertIn('styles.css', result)
        self.assertIn('script.js', result)
        self.assertIn('index.html', result)
        self.assertIn('setup.sh', result)

        # Check if ignored file is not included
        self.assertNotIn('readme.txt', result)

        # Check if file contents are correctly included
        self.assertIn('print("Hello, World!")', result)
        self.assertIn('body { color: blue; }', result)
        self.assertIn('console.log("JavaScript")', result)
        self.assertIn('<h1>Hello</h1>', result)
        self.assertIn('echo "Setup complete"', result)

        # Check if the output format instructions are included
        self.assertIn('<filename_extension>File content goes here</filename_extension>', result)
        self.assertIn('<myfile_py>print(\'Hello, World!\')</myfile_py>', result)

        # Check if the objective and notes are included
        self.assertIn('# Objective', result)
        self.assertIn('# Output', result)
        self.assertIn('## Note', result)

    def test_empty_folder(self):
        empty_dir = tempfile.TemporaryDirectory()
        self.addCleanup(empty_dir.cleanup)

        result = load_code_folder_to_system_prompt(empty_dir.name)

        # Check if the basic structure is still there
        self.assertIn('# Example Project', result)
        self.assertIn('# Objective', result)
        self.assertIn('# Output', result)

        # Check that no file contents are included
        self.assertNotIn('```', result)

if __name__ == '__main__':
    unittest.main()