# -*- coding: utf-8 -*-
import platform
import os
import sys

from thonny.code import get_saved_current_script_filename
from thonny import get_runner, terminal, get_workbench
from thonny.common import get_exe_dirs, get_augmented_system_path
from thonny.running import get_environment_overrides_for_python_subprocess

def _open_system_shell():
    """Main task is to modify path and open terminal window.
    Bonus (and most difficult) part is executing a script in this window
    for recommending commands for running given python and related pip"""
    
    filename = get_saved_current_script_filename(force=False)
    if filename:
        cwd = os.path.dirname(filename)
    else:
        cwd = None
    
    proxy = get_runner().get_backend_proxy()
    if proxy and proxy.get_local_executable():
        target_executable = proxy.get_local_executable()
    else:
        target_executable = sys.executable
    
    exe_dirs = get_exe_dirs()
    if hasattr(proxy, "get_exe_dirs") and proxy.get_exe_dirs():
        # use both backend and frontend exe dirs
        exe_dirs = proxy.get_exe_dirs() + exe_dirs
    
    env_overrides = get_environment_overrides_for_python_subprocess(
        target_executable)
    env_overrides["PATH"] = get_augmented_system_path(exe_dirs) 
    
    explainer = os.path.join(os.path.dirname(__file__), "explain_environment.py")
    cmd = [target_executable, explainer]
    
    activate = os.path.join(os.path.dirname(target_executable), 
                            "activate.bat" if platform.system() == "Windows"
                            else "activate")
    
    if os.path.isfile(activate):
        del env_overrides["PATH"]
        if platform.system() == "Windows":
            cmd = [activate, "&"] + cmd
        else:
            cmd = ["source", activate, ";"] + cmd 
        
    return terminal.run_in_terminal(cmd, cwd, env_overrides, True)

def load_plugin() -> None:
    get_workbench().add_command(
        "OpenSystemShell",
        "tools",
        "Open system shell...",
        _open_system_shell,
        group=80,
        image="terminal"
    )
