import sys
import json
import os.path
from typing import Final, Dict, Any

if getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(sys.executable))

FILE_PATH: Final = os.path.join(sys.path[0], "config.json")

if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w") as f:
        f.write("{}")

class Config:
    def __init__(self, data: Dict):
        self.MAVEN_PATH = data.get("MAVEN_PATH", None)
        self.VERSION_TO_USE = data.get("VERSION_TO_USE", None)

    def as_dict(self):
        return dict(MAVEN_PATH = self.MAVEN_PATH, VERSION_TO_USE = self.VERSION_TO_USE)

def get_config() -> Config:
    with open(FILE_PATH, "r") as file:
        config = json.loads(file.read(), object_hook=lambda data: Config(data))

    if not config.MAVEN_PATH:
        path = input("Path where mvm will install the Maven versions: ")
        config.MAVEN_PATH = path
        save_config(config)
    return config

def save_config(config: Config):
    file: Any
    with open(FILE_PATH, "w") as file:
        json.dump(config.as_dict(), file, indent=4, sort_keys=True)