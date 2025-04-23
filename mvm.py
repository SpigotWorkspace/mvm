import os
import re
import subprocess
import sys
import import_config

config = import_config.get_config()
MAVEN_PATH = config.MAVEN_PATH
if not os.path.exists(MAVEN_PATH):
    print(f"Maven path '{MAVEN_PATH}' does not exist")
    sys.exit(1)

with os.scandir(MAVEN_PATH) as it:
    for folder in it:
        mvn_path = os.path.join(folder.path, "bin", "mvn")
        is_executable = os.path.exists(mvn_path)

        if not is_executable: continue

        process = subprocess.run([mvn_path, "-v"], check=True, capture_output=True, shell=True, text=True)

        version_line = process.stdout.splitlines()[0]
        version = re.search(r"(\d+\.\d+\.\d+)", version_line).group(1)
        print(version)