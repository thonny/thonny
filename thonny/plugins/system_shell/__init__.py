# -*- coding: utf-8 -*-
from thonny.globals import get_workbench
from subprocess import Popen
import sys
import os.path
import shlex
import platform


def open_system_shell():
    if platform.system() == "Windows":
        open_system_shell_windows()
    else:
        open_system_shell_unix()

def open_system_shell_unix():
    env = os.environ.copy()
    path = env.get("PATH", "")
    env["PATH"] = os.path.join(sys.exec_prefix, "bin") + os.pathsep + path
                   
    explainer = os.path.join(os.path.dirname(__file__), "explain_environment.py")
    
#    Popen("""osascript -e 'tell application "Terminal" to do script "%s"'""" 
    #Popen("""open -a Terminal . ; osascript -e 'tell application "Terminal" to activate in window 1' """, env=env, shell=True) 
    
    Popen("""osascript -e 'tell application "Terminal" to do script "%s %s"' ;  osascript -e 'tell application "Terminal" to activate'""" 
          % (sys.executable, explainer)
          ,
          env=env, shell=True)

    #script = os.path.join(os.path.dirname(__file__), "scr.scpt")
    #Popen(["/usr/bin/osascript",  script] 
    #      #% explainer
    #      ,env=env, shell=False)

def open_system_shell_windows():
    env = os.environ.copy()
    path = env.get("PATH", "")
    env["PATH"] = (sys.exec_prefix + os.pathsep
                   + os.path.join(sys.exec_prefix, "Scripts") + os.pathsep
                   + path)
    
    explainer = os.path.join(os.path.dirname(__file__), "explain_python_env.bat")
    explainer = os.path.join(os.path.dirname(__file__), "explain_environment.py")
    Popen('start "Shell for using %s" /W cmd /K "%s" %s' % 
          (sys.exec_prefix, sys.executable, explainer),
          env=env, shell=True)
    

def load_plugin():
    get_workbench().add_command("OpenSystemShell", "tools", "Open system shell",
                    open_system_shell, group=80)