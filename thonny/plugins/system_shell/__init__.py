# -*- coding: utf-8 -*-
from subprocess import Popen, check_output
import os.path
import shlex
import platform
from tkinter.messagebox import showerror
import shutil
from thonny.globals import get_runner
from thonny.running import get_gui_interpreter

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
    # Always prepending to path may seem better, but this could mess up other things.
    # If the directory contains only one Python distribution executables, then 
    # it probably won't be in path yet and therefore will be prepended.
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
    if python_interpreter == get_gui_interpreter():
        # in gui environment make "pip install"
        # use a folder outside thonny installation
        # in order to keep packages after reinstalling Thonny 
        env["PIP_USER"] = "true"
        env["PYTHONUSERBASE"] = os.path.expanduser(os.path.join("~", ".thonny"))
    
    # TODO: what if executable or explainer needs escaping?
    # Maybe try creating a script in temp folder and execute this,
    # passing required paths via environment variables.
    
    interpreter=python_interpreter.replace("pythonw","python")
    explainer=os.path.join(os.path.dirname(__file__), "explain_environment.py")
    cwd=get_runner().get_cwd()
    
    if platform.system() == "Windows":
        env["PATH"] = _add_to_path(exec_prefix + os.pathsep, env.get("PATH", ""))
        env["PATH"] = _add_to_path(os.path.join(exec_prefix, "Scripts"), env.get("PATH", ""))
        # Command line will be something like:
        # start "Shell for {interpreter}" /D "{cwd}" /W cmd /K "{interpreter}" {explainer}
        # I'm using list method to avoid quoting problems (last argument can't be quoted)
        cmd_line = ['start',
                    'Shell for %s' % interpreter,
                    '/D',
                    cwd,
                    '/W',
                    'cmd',
                    '/K',
                    interpreter,
                    explainer] 
        Popen(cmd_line, env=env, shell=True)
        
    elif platform.system() == "Linux":
        env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])
        if shutil.which("x-terminal-emulator"):
            cmd = "x-terminal-emulator"
# Can't use konsole, because it doesn't pass on the environment
#         elif shutil.which("konsole"):
#             if (shutil.which("gnome-terminal") 
#                 and "gnome" in os.environ.get("DESKTOP_SESSION", "").lower()):
#                 cmd = "gnome-terminal"
#             else:
#                 cmd = "konsole"
        elif shutil.which("gnome-terminal"):
            cmd = "gnome-terminal"
        elif shutil.which("terminal"): # XFCE?
            cmd = "terminal"
        elif shutil.which("xterm"):
            cmd = "xterm"
        else:
            raise RuntimeError("Don't know how to open terminal emulator")
        # http://stackoverflow.com/a/4466566/261181
        cmd_line = (cmd + """ -e 'bash -c "{interpreter} {explainer};exec bash -i"' """
                    .format(interpreter=interpreter, explainer=explainer))
        Popen(cmd_line, env=env, shell=True)
        
    elif platform.system() == "Darwin":
        env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])
        # Need to modify environment explicitly as "tell application" won't pass the environment
        # (at least when Terminal is already active)
        
        # TODO: osascript won't change Terminal-s env
        # At the moment I just explicitly set important variables
        if "PIP_USER" in env:
            pip_tweak = ';export PIP_USER={PIP_USER};export PYTHONUSERBASE={PYTHONUSERBASE}'.format(**env)
        else:
            pip_tweak = ''
        cmd_line = (("osascript"
            + """ -e 'tell application "Terminal" to do script "unset TK_LIBRARY; unset TCL_LIBRARY; PATH=%s %s; {interpreter} {explainer}"'"""
            + """ -e 'tell application "Terminal" to activate'"""
            ) % (env["PATH"], pip_tweak)
        ).format(interpreter=interpreter, explainer=explainer)

        # TODO: at the moment two new terminal windows will be opened when terminal is not already active
        # https://discussions.apple.com/thread/1738507?tstart=0
        # IDEA: detect if terminal is already active and do "do script ... in front window" if not
        # (but seems that sometimes it can't find this "front window")
        Popen(cmd_line, env=env, shell=True)

    
    else:
        showerror("Problem", "Don't know how to open system shell on this platform (%s)"
                  % platform.system())
        return
    

    

def load_plugin():
    from thonny.globals import get_workbench
    from thonny.running import get_selected_interpreter
    
    def open_system_shell_for_selected_interpreter(): 
        open_system_shell(get_selected_interpreter())
    
    get_workbench().add_command("OpenSystemShell", "tools", "Open system shell",
                    open_system_shell_for_selected_interpreter, group=80)