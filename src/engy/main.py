import argparse
import os
import subprocess
import sys
from contextlib import contextmanager

import yaml

from .app_builder import (
    generate_all,
    generate_backend_unit_tests,
    generate_dockerfile,
    regenerate_all,
    regenerate_backend,
    regenerate_frontend,
)
from .app_cloner import clone_all
from .app_split import split
from .util import assert_file_exists_and_read, run_docker


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


def diff_list(current_list, goal_list):
    current_list = current_list or []
    goal_list = goal_list or []
    current_set = set(current_list)
    goal_set = set(goal_list)
    added = goal_set - current_set
    removed = current_set - goal_set
    return list(added), list(removed)


def diff_configs():
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as file:
            goal_config = yaml.safe_load(file)
    else:
        goal_config = {}

    if os.path.exists("state.yaml"):
        with open("state.yaml", "r") as file:
            current_config = yaml.safe_load(file)
    else:
        current_config = {}

    new_features, removed_features = diff_list(
        current_config.get("features", []), goal_config.get("features", [])
    )
    new_bugs, removed_bugs = diff_list(
        current_config.get("bugs", []), goal_config.get("bugs", [])
    )
    return new_features, removed_features, new_bugs, removed_bugs


def main():
    parser = argparse.ArgumentParser(
        description="Generate python webapp from prompts. (require either `input.txt` or `config.yaml`)"
    )
    parser.add_argument(
        "--log-to-file", action="store_true", help="Log output to terminal.log"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    backend_parser = subparsers.add_parser("backend", help="Regenerate the backend")
    frontend_parser = subparsers.add_parser("frontend", help="Regenerate the frontend")
    bug_parser = subparsers.add_parser("bug", help="Fix the bug in bug.txt")
    feature_parser = subparsers.add_parser(
        "feature", help="Add the feature stated in feature.txt"
    )
    clone_parser = subparsers.add_parser(
        "clone", help="Clone a new engy app based on existing engy app"
    )
    clone_parser.add_argument("path", type=str, help="path to clone")
    diff_parser = subparsers.add_parser(
        "diff", help="Diff between current and goal configurations (config.yaml)"
    )
    apply_parser = subparsers.add_parser(
        "apply", help="Apply diff to match goal configurations (config.yaml)"
    )
    docker_parser = subparsers.add_parser("docker", help="Generate Dockerfile")
    run_docker_parser = subparsers.add_parser("run_docker", help="Generate Dockerfile")
    refactor_parser = subparsers.add_parser(
        "refactor", help="Refactor the frontend and backend into modular files"
    )
    split_parser = subparsers.add_parser(
        "split", help="Split the frontend and backend into modular files"
    )
    backend_unit_tests_parser = subparsers.add_parser(
        "unit_tests", help="Generate backend unit tests"
    )

    args = parser.parse_args()

    with log_to_file(args.log_to_file):
        if args.subcommand == "backend":
            prompts = input("Input prompts:")
            regenerate_backend(prompts)
        elif args.subcommand == "frontend":
            prompts = input("Input prompts:")
            regenerate_frontend(prompts)
        elif args.subcommand == "bug":
            bug_description = assert_file_exists_and_read("bug.txt")
            prompts = f"Fix bug:\n<BUG>\n{bug_description}\n</BUG>"
            regenerate_all(prompts)
        elif args.subcommand == "feature":
            feature_description = assert_file_exists_and_read("feature.txt")
            prompts = f"<FEATURE_REQUEST>\n{feature_description}\n</FEATURE_REQUEST>"
            regenerate_all(prompts)
        elif args.subcommand == "clone":
            print(f"Clone project {args.path}")
            if not os.path.exists("input.txt"):
                parser.print_help()
                sys.exit(1)
            input_prompts = assert_file_exists_and_read("input.txt")
            clone_all(args.path, input_prompts)
        elif args.subcommand == "diff":
            print("Diff configs")
            new_features, removed_features, new_bugs, removed_bugs = diff_configs()
            print("Adding features:", new_features)
            print("Removing features:", removed_features)
            print("Adding bugs:", new_bugs)
        elif args.subcommand == "apply":
            print("Apply diff")
            new_features, removed_features, new_bugs, removed_bugs = diff_configs()
            print("Adding features:", new_features)
            print("Removing features:", removed_features)
            print("Adding bugs:", new_bugs)
            bugs_prompt = "\n".join(
                [f"Fix bug:\n<BUG>\n{bug}\n</BUG>" for bug in new_bugs]
            )
            add_features_prompt = "\n".join(
                [
                    f"<FEATURE_REQUEST>\n{feature}\n</FEATURE_REQUEST>"
                    for feature in new_features
                ]
            )
            remove_features_prompt = "\n".join(
                [
                    f"<FEATURE_REQUEST>\nRemove feature '{feature}'\n</FEATURE_REQUEST>"
                    for feature in removed_features
                ]
            )
            prompts = bugs_prompt + add_features_prompt + remove_features_prompt
            print(f"{prompts=}")
            regenerate_all(prompts)
            with open("state.yaml", "w") as file:
                yaml.dump(
                    {"features": new_features, "bugs": new_bugs},
                    file,
                    default_flow_style=False,
                )
        elif args.subcommand == "docker":
            generate_dockerfile()
        elif args.subcommand == "run_docker":
            run_docker()
        elif args.subcommand == "unit_tests":
            generate_backend_unit_tests()
        elif args.subcommand == "split":
            split()
        else:
            print("App builder")
            if not os.path.exists("input.txt"):
                parser.print_help()
                sys.exit(1)
            input_prompts = assert_file_exists_and_read("input.txt")
            generate_all(input_prompts)


if __name__ == "__main__":
    main()
