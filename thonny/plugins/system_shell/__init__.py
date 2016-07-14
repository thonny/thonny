# -*- coding: utf-8 -*-
from subprocess import Popen, check_output
import os.path
import shlex
import platform
from tkinter.messagebox import showerror
import shutil

def _create_pythonless_environment():
    # If I want to call another python version, then 
    # I need to remove from environment the items installed by current interpreter
    env = {}
    
    for key in os.environ:
        if ("python" not in key.lower()
            and key not in ["TK_LIBRARY", "TCL_LIBRARY"]):
            env[key] = os.environ[key]
    
    return env


def _get_exec_prefix(python_interpreter):
    
    return check_output([python_interpreter, "-c", "import sys; print(sys.exec_prefix)"],
                        universal_newlines=True,
                        env=_create_pythonless_environment()
                        ).strip()

def _add_to_path(directory, path):
    if (directory in path.split(os.pathsep)
        or platform.system() == "Windows" and directory.lower() in path.lower().split(os.pathsep)):
        return path
    else:
        return directory + os.pathsep + path

def open_system_shell(python_interpreter):
    """Main task is to modify path and open terminal window.
    Bonus (and most difficult) part is executing a script in this window
    for recommending commands for running given python and related pip"""
    
    exec_prefix=_get_exec_prefix(python_interpreter)
    env = _create_pythonless_environment()
    
    # TODO: what if executable or explainer needs escaping?
    # Maybe try creating a script in temp folder and execute this,
    # passing required paths via environment variables.
    
    if platform.system() == "Windows":
        env["PATH"] = _add_to_path(exec_prefix + os.pathsep, env.get("PATH", ""))
        env["PATH"] = _add_to_path(os.path.join(exec_prefix, "Scripts"), env.get("PATH", ""))
        cmd_line = 'start "Shell for {interpreter}" /W cmd /K "{interpreter}" {explainer}'
        
    elif platform.system() == "Linux":
        env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])
        if shutil.which("x-terminal-emulator"):
            cmd = "x-terminal-emulator"
        elif shutil.which("gnome-terminal"):
            cmd = "gnome-terminal"
        elif shutil.which("konsole"):
            cmd = "konsole"
        else:
            raise RuntimeError("Don't know how to open terminal emulator")
        # http://stackoverflow.com/a/4466566/261181
        cmd_line = cmd + """ -e 'bash -c "{interpreter} {explainer};exec bash -i"'"""
        
    elif platform.system() == "Darwin":
        env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])
        # Need to modify environment explicitly as "tell application" won't pass the environment
        # (at least when Terminal is already active)
        cmd_line = ("osascript"
            + """ -e 'tell application "Terminal" to do script "unset TK_LIBRARY; unset TCL_LIBRARY; PATH=%s; {interpreter} {explainer}"'"""
            + """ -e 'tell application "Terminal" to activate'"""
        ) % env["PATH"]

        # TODO: at the moment two new terminal windows will be opened when terminal is not already active
        # https://discussions.apple.com/thread/1738507?tstart=0
        # IDEA: detect if terminal is already active and do "do script ... in front window" if not
        # (but seems that sometimes it can't find this "front window")

    
    else:
        showerror("Problem", "Don't know how to open system shell on this platform (%s)"
                  % platform.system())
        return
    
    
    expanded_cmd_line = cmd_line.format(interpreter=python_interpreter.replace("pythonw","python"),
                          explainer=os.path.join(os.path.dirname(__file__), "explain_environment.py"))
    print(expanded_cmd_line) 
    Popen(expanded_cmd_line, env=env, shell=True)

    

def load_plugin():
    from thonny.globals import get_workbench
    from thonny.running import get_selected_interpreter
    
    def open_system_shell_for_selected_interpreter(): 
        open_system_shell(get_selected_interpreter())
    
    get_workbench().add_command("OpenSystemShell", "tools", "Open system shell",
                    open_system_shell_for_selected_interpreter, group=80)