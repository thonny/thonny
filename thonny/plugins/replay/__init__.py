import os.path
import sys
import subprocess
from thonny.globals import get_workbench

def load_plugin():
    def cmd_show_replayer():
        launcher = os.path.join(get_workbench().main_dir, "thonny", "plugins", "replay")
        cmd_line = [sys.executable, '-u', launcher]
        subprocess.Popen(cmd_line)
        
    get_workbench().add_command("open_replayer", "view", "Open replayer", cmd_show_replayer)    
    
    