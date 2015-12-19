# -*- coding: utf-8 -*-
from thonny.globals import get_workbench
from subprocess import Popen
import sys
import os.path
import shlex

_CURRENT_PYTHON_EXEC_PREFIX = "CURRENT_PYTHON_EXEC_PREFIX"

def prepare_windows_environment():
    # In Windows, Python binaries are in different directories
    # and those directories contain only Python related stuff,
    # so it's safe to 
    env = os.environ.copy()
    
    def keep_path_item(x):
        dir_path = shlex.split()[0] 
        dir_items = set(os.listdir(dir_path))
        forbidden_items = {"python", "pythonw",
                           "python3", "python2.7"}
        #if  
    
    path_items = filter(keep_path_item, env.get("PATH", "").split(os.pathsep))
    
    current_interpreter_bin_dir = ...
    path_items.insert(0, ) 

def explain_python_environment():
    assert _CURRENT_PYTHON_EXEC_PREFIX in os.environ
    print("This session is prepared for using Python installation in")
    print(os.environ[_CURRENT_PYTHON_EXEC_PREFIX])
    print()
    print("Some important commands and their full paths")

def open_system_shell():
    env = os.environ.copy()
    path = env.get("PATH", "")
    env["PATH"] = (sys.exec_prefix + os.pathsep
                   + os.path.join(sys.exec_prefix, "Scripts") + os.pathsep
                   + path)
    env["CURRENT_PYTHON_EXEC_PREFIX"] = sys.exec_prefix
                   
    explainer = os.path.join(os.path.dirname(__file__), "explain_python_env.bat")
    
    Popen('start "Shell for using %s" /w "%s" rrr' % (sys.exec_prefix, explainer),
          env=env, shell=True)

def load_plugin():
    get_workbench().add_command("OpenSystemShell", "tools", "Open system shell",
                    open_system_shell, group=80)