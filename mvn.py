import subprocess
import sys
import os
from typing import List

def execute(path: str, commands: List[str]) -> str:
    process = subprocess.run([path] + commands, capture_output=True, shell=True, text=True)
    return process.stdout

if __name__ == "__main__":
    import import_config
    config = import_config.get_config()
    if not config.VERSION_TO_USE:
        print("No default version set. Please use 'mvm use' to select a default version.")
        sys.exit(1)
    MAVEN_HOME_PATH = os.path.join(config.VERSION_TO_USE, "bin", "mvn")
    if not os.path.exists(MAVEN_HOME_PATH):
        print(
            f"Command cannot be executed because '{MAVEN_HOME_PATH}' does not exist.\n"
            f"Please use 'mvm use' to select a valid version."
        )
        sys.exit(1)

    output = execute(MAVEN_HOME_PATH, sys.argv[1:])
    print(output)
