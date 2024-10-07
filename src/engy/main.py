import argparse
import sys
from contextlib import contextmanager

from .app_builder import (generate_all, regenerate_all, regenerate_backend,
                          regenerate_frontend)
from .app_cloner import clone_all
from .util import assert_file_exists_and_read


@contextmanager
def log_to_file(should_log):
    if should_log:
        log_file = open("terminal.log", "a")
        original_stdout = sys.stdout
        sys.stdout = log_file
    try:
        yield
    finally:
        if should_log:
            sys.stdout = original_stdout
            log_file.close()


def main():
    parser = argparse.ArgumentParser(
        description="Application with subcommands")
    parser.add_argument("--log-to-file", action="store_true",
                        help="Log output to terminal.log")
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    backend_parser = subparsers.add_parser(
        "backend", help="Regenerate the backend")
    frontend_parser = subparsers.add_parser(
        "frontend", help="Regenerate the frontend")
    iter_parser = subparsers.add_parser(
        "iter", help="Regenerate both backend/frontend")
    bug_parser = subparsers.add_parser(
        "bug", help="Fix the bug in bug.txt")
    feature_parser = subparsers.add_parser(
        "feature", help="Add the feature stated in feature.txt")
    clone_parser = subparsers.add_parser(
        "clone", help="Continue dev based on existing finapp")
    clone_parser.add_argument('path', type=str, help='path to clone')

    args = parser.parse_args()
    input_prompts = assert_file_exists_and_read('input.txt')
    with log_to_file(args.log_to_file):
        if args.subcommand == "backend":
            prompts = input("Input prompts:")
            regenerate_backend(prompts)
        elif args.subcommand == "frontend":
            prompts = input("Input prompts:")
            regenerate_frontend(prompts)
        elif args.subcommand == "iter":
            prompts = input("Input prompts:")
            regenerate_all(prompts)
        elif args.subcommand == "bug":
            bug_description = assert_file_exists_and_read('bug.txt')
            prompts = f'Fix bug:\n<BUG>\n{bug_description}\n</BUG>'
            regenerate_all(prompts)
        elif args.subcommand == "feature":
            feature_description = assert_file_exists_and_read('feature.txt')
            prompts = f'<FEATURE_REQUEST>\n{feature_description}\n</FEATURE_REQUEST>'
            regenerate_all(prompts)
        elif args.subcommand == "clone":
            print(f'Clone project {args.path}')
            clone_all(args.path, input_prompts)
        else:
            print('App builder')
            generate_all(input_prompts)


if __name__ == "__main__":
    main()
