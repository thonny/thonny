# -*- coding: utf-8 -*-
from subprocess import Popen, check_output
import os.path
import shlex
import platform
from tkinter.messagebox import showerror
from thonny.plugins.system_shell.explain_environment import create_pythonless_environment

def _get_exec_prefix(python_interpreter):
    
    return check_output([python_interpreter, "-c", "import sys; print(sys.exec_prefix)"],
                        universal_newlines=True,
                        env=create_pythonless_environment()
                        ).strip()

def open_system_shell(python_interpreter):
    """Main task is to modify path and open terminal window.
    Bonus (and most difficult) part is executing a script in this window
    for recommending commands for running given python and related pip"""
    
    print("Asking prefix for", python_interpreter)
    exec_prefix=_get_exec_prefix(python_interpreter)
    print("Got", exec_prefix)
    env = create_pythonless_environment()
    path = env.get("PATH", "")
    
    # TODO: what if executable or explainer needs escaping?
    # Maybe try creating a script in temp folder and execute this,
    # passing required paths via environment variables.
    
    if platform.system() == "Windows":
        env["PATH"] = (exec_prefix + os.pathsep
                       + os.path.join(exec_prefix, "Scripts") + os.pathsep
                       + path)
        cmd_line = 'start "Shell for {interpreter}" /W cmd /K "{interpreter}" {explainer}'
        
    elif platform.system() == "Linux":
        env["PATH"] = os.path.join(exec_prefix, "bin") + os.pathsep + path
        cmd_line = """x-terminal-emulator -e 'bash -c "{interpreter} {explainer}" ;bash'"""
        
    elif platform.system() == "Darwin":
        env["PATH"] = os.path.join(exec_prefix, "bin") + os.pathsep + path
        cmd_line = """osascript -e 'tell application "Terminal" to do script "{interpreter} {explainer}"' ;  osascript -e 'tell application "Terminal" to activate'"""
    
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