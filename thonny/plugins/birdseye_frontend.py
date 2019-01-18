import os.path
from thonny import get_workbench, get_runner
import subprocess
import sys

def _start_debug_enabled():
    return (get_workbench().get_editor_notebook().get_current_editor() is not None
        and "debug" in get_runner().get_supported_features())

def _debug_with_birdseye():
    # TODO: can you change birdseye command such that it doesn't 
    # start the server if it is already started?
    subprocess.Popen([sys.executable, "-m", "birdseye"])
    get_runner().execute_current("Birdseye")

# order_key makes the plugin to be loaded later than other same tier plugins
# This way it gets positioned after main debug commands in the Run menu
load_order_key = "zz"

def load_plugin():
    get_workbench().add_command(
        "birdseye",
        "run",
        "Debug current script (birdseye)",
        _debug_with_birdseye,
        caption="birdseye",
        tester=_start_debug_enabled,
        default_sequence="<Control-B>",
        group=10,
        image=os.path.join(os.path.dirname(__file__), "..", "res", "birdseye.png"),
    )