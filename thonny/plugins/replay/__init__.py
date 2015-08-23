import os.path
import sys
import subprocess

def load_plugin():
    def _cmd_show_replayer():
        launcher = os.path.join(workbench.main_dir, "thonny", "plugins", "replay")
        cmd_line = [sys.executable, '-u', launcher]
        subprocess.Popen(cmd_line)
        
    get_workbench().add_command("open_replayer", "view", "Open replayer", cmd_show_replayer)    
    
    