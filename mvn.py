import subprocess
import sys
import os
import import_config

config = import_config.get_config()
MAVEN_HOME_PATH = os.path.join(config.VERSION_TO_USE, "bin", "mvn")
process = subprocess.run([MAVEN_HOME_PATH] + sys.argv[1:], check=True, capture_output=True, shell=True, text=True)
print(process.stdout)