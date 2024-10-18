import os
import shutil
import unittest
from pathlib import Path
from textwrap import dedent

from .produce_files import produce_files


class TestProduceFiles(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        os.chdir(self.test_dir)

    def tearDown(self):
        # Change back to the parent directory and remove the test directory
        os.chdir("..")
        shutil.rmtree(self.test_dir)

    def test_predefined_mapping(self):
        test_content = dedent("""
        <AGENTS_DESIGN>
        {"agent": "test"}
        </AGENTS_DESIGN>
        """)
        produce_files(test_content)
        self.assertTrue(Path("agents_design.json").exists())
        with open("agents_design.json", "r") as f:
            self.assertEqual(f.read().strip(), '{"agent": "test"}')

    def test_custom_block(self):
        test_content = dedent("""
        <custom_script_py>
        print("Hello, World!")
        </custom_script_py>
        """)
        produce_files(test_content)
        self.assertTrue(Path("custom_script.py").exists())
        with open("custom_script.py", "r") as f:
            self.assertEqual(f.read().strip(), 'print("Hello, World!")')

    def test_multiple_blocks(self):
        test_content = dedent("""
        <AGENTS_DESIGN>
        {"agent": "test"}
        </AGENTS_DESIGN>
        <custom_script_py>
        print("Hello, World!")
        </custom_script_py>
        <another_file_txt>
        This is another test file.
        </another_file_txt>
        """)
        produce_files(test_content)
        self.assertTrue(Path("agents_design.json").exists())
        self.assertTrue(Path("custom_script.py").exists())
        self.assertTrue(Path("another_file.txt").exists())

    def test_no_matching_blocks(self):
        test_content = "This content has no blocks to produce files."
        produce_files(test_content)
        self.assertEqual(len(list(Path().glob("*"))), 0)

    def test_empty_block(self):
        test_content = dedent("""
        <empty_file_txt></empty_file_txt>
        """)
        produce_files(test_content)
        self.assertTrue(Path("empty_file.txt").exists())
        with open("empty_file.txt", "r") as f:
            self.assertEqual(f.read(), "")


if __name__ == "__main__":
    unittest.main()
