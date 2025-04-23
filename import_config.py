import sys, os

if getattr(sys, "frozen", False):
    sys.path.append(os.path.dirname(sys.executable))

import config

def get_config():
    return config