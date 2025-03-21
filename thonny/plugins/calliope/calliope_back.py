import os.path
import sys
from logging import getLogger
from typing import List, Optional

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.insert(0, thonny_container)

from thonny.plugins.micropython.bare_metal_backend import launch_bare_metal_backend
from thonny.plugins.simplified_micropython.simplified_mp_back import SimplifiedMicroPythonBackend

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.calliope.calliope_back")


class CalliopeMiniMicroPythonBackend(SimplifiedMicroPythonBackend):
    pass


if __name__ == "__main__":
    launch_bare_metal_backend(CalliopeMiniMicroPythonBackend)
