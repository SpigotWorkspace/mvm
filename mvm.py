import argparse
import os
import re
import sys
from typing import Set

import import_config
import mvn

config = import_config.get_config()
MAVEN_PATH = config.MAVEN_PATH
if not os.path.exists(MAVEN_PATH):
    print(f"Maven path '{MAVEN_PATH}' does not exist")
    sys.exit(1)

def scan_versions():
    versions: Set[str] = set()
    with os.scandir(MAVEN_PATH) as it:
        for folder in it:
            mvn_path = os.path.join(folder.path, "bin", "mvn")
            is_executable = os.path.exists(mvn_path)

            if not is_executable: continue

            command_output = mvn.execute(mvn_path, ["-v"])
            version_line = command_output.splitlines()[0]
            version = re.search(r"(\d+\.\d+\.\d+)", version_line).group(1)
            versions.add(version)
    return versions

def list_command(_):
    versions = scan_versions()
    for version in versions:
        print(f"- {version}")

parser = argparse.ArgumentParser('mvm')
subparsers = parser.add_subparsers()

parser_list = subparsers.add_parser('list', help='lists all installed versions under config.MAVEN_PATH')
parser_list.set_defaults(func=list_command)

args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)