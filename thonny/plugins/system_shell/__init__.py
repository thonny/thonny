# -*- coding: utf-8 -*-
from subprocess import Popen, check_output
import os.path
import shlex
import platform
from tkinter.messagebox import showerror
import shutil
from thonny.globals import get_runner
from thonny import THONNY_USER_DIR
import subprocess
from time import sleep

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

def open_system_shell():
    """Main task is to modify path and open terminal window.
    Bonus (and most difficult) part is executing a script in this window
    for recommending commands for running given python and related pip"""
    python_interpreter = get_runner().get_interpreter_command()
    if python_interpreter is None:
        return
    
    exec_prefix=_get_exec_prefix(python_interpreter)
    if ".." in exec_prefix:
        exec_prefix = os.path.realpath(exec_prefix)
    env = _create_pythonless_environment()
    
    # TODO: take care of SSL_CERT_FILE (unset when running external python and set for builtin)
    # Unset when we're in builtin python and target python is external
    
    # TODO: what if executable or explainer needs escaping?
    # Maybe try creating a script in temp folder and execute this,
    # passing required paths via environment variables.
    
    interpreter=python_interpreter.replace("pythonw","python")
    explainer=os.path.join(os.path.dirname(__file__), "explain_environment.py")
    cwd=get_runner().get_cwd()
    
    if platform.system() == "Windows":
        return _open_shell_in_windows(cwd, env, interpreter, explainer, exec_prefix)
        
    elif platform.system() == "Linux":
        return _open_shell_in_linux(cwd, env, interpreter, explainer, exec_prefix)
        
    elif platform.system() == "Darwin":
        _open_shell_in_macos(cwd, env, interpreter, explainer, exec_prefix)
    else:
        showerror("Problem", "Don't know how to open system shell on this platform (%s)"
                  % platform.system())
        return

def _open_shell_in_windows(cwd, env, interpreter, explainer, exec_prefix):
    env["PATH"] = _add_to_path(exec_prefix + os.pathsep, env.get("PATH", ""))
    env["PATH"] = _add_to_path(os.path.join(exec_prefix, "Scripts"), env.get("PATH", ""))
    
    # Yes, the /K argument has weird quoting. Can't explain this, but it works 
    cmd_line = """start "Shell for {interpreter}" /D "{cwd}" /W cmd /K ""{interpreter}" "{explainer}"" """.format(
        interpreter=interpreter, 
        cwd=cwd,
        explainer=explainer)
    
    Popen(cmd_line, env=env, shell=True)

def _open_shell_in_linux(cwd, env, interpreter, explainer, exec_prefix):
    def _shellquote(s):
        return subprocess.list2cmdline([s])

    # No escaping in PATH possible: http://stackoverflow.com/a/29213487/261181
    # (neither necessary except for colon)
    env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])
    
    if shutil.which("x-terminal-emulator"):
        term_cmd = "x-terminal-emulator"
# Can't use konsole, because it doesn't pass on the environment
#         elif shutil.which("konsole"):
#             if (shutil.which("gnome-terminal") 
#                 and "gnome" in os.environ.get("DESKTOP_SESSION", "").lower()):
#                 term_cmd = "gnome-terminal"
#             else:
#                 term_cmd = "konsole"
    elif shutil.which("gnome-terminal"):
        term_cmd = "gnome-terminal"
    elif shutil.which("terminal"): # XFCE?
        term_cmd = "terminal"
    elif shutil.which("xterm"):
        term_cmd = "xterm"
    else:
        raise RuntimeError("Don't know how to open terminal emulator")
    
    # Need to prevent shell from closing after executing the command:
    # http://stackoverflow.com/a/4466566/261181
    core_cmd = "{interpreter} {explainer}; exec bash -i".format(interpreter=_shellquote(interpreter),
                                                                    explainer=_shellquote(explainer))
    in_term_cmd = "bash -c {core_cmd}".format(core_cmd=_shellquote(core_cmd))
    whole_cmd = "{term_cmd} -e {in_term_cmd}".format(term_cmd=term_cmd,
                                                     in_term_cmd=_shellquote(in_term_cmd))
   
    Popen(whole_cmd, env=env, shell=True)

def _open_shell_in_macos(cwd, env, interpreter, explainer, exec_prefix):
    _shellquote = shlex.quote
    
    # No quoting inside Linux PATH variable is possible: http://stackoverflow.com/a/29213487/261181
    # (neither necessary except for colon)
    # Assuming this applies for OS X as well
    env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])
    
    # osascript "tell application" won't change Terminal's env
    # (at least when Terminal is already active)
    # At the moment I just explicitly set some important variables
    # TODO: Did I miss something?
    cmd = "PATH={}; unset TK_LIBRARY; unset TCL_LIBRARY".format(_shellquote(env["PATH"]))
    
    if "SSL_CERT_FILE" in env:
        cmd += ";export SSL_CERT_FILE=" + _shellquote(env["SSL_CERT_FILE"])
        
    cmd += "; {interpreter} {explainer}".format(
        interpreter=_shellquote(interpreter),
        explainer=_shellquote(explainer))
    
    # The script will be sent to Terminal with 'do script' command, which takes a string.
    # We'll prepare an AppleScript string literal for this
    # (http://stackoverflow.com/questions/10667800/using-quotes-in-a-applescript-string):
    cmd_as_apple_script_string_literal = ('"' 
                                             + cmd
                                             .replace("\\", "\\\\")
                                             .replace('"', '\\"') 
                                             + '"')
    
    # When Terminal is not open, then do script opens two windows.
    # do script ... in window 1 would solve this, but if Terminal is already
    # open, this could run the script in existing terminal (in undesirable env on situation)
    # That's why I need to prepare two variations of the 'do script' command
    doScriptCmd1 = """        do script %s """             % cmd_as_apple_script_string_literal
    doScriptCmd2 = """        do script %s in window 1 """ % cmd_as_apple_script_string_literal
    
    # The whole AppleScript will be executed with osascript by giving script
    # lines as arguments. The lines containing our script need to be shell-quoted:
    quotedCmd1 = subprocess.list2cmdline([doScriptCmd1])
    quotedCmd2 = subprocess.list2cmdline([doScriptCmd2])
    
    # Now we can finally assemble the osascript command line
    cmd_line = ("osascript"
        + """ -e 'if application "Terminal" is running then ' """
        + """ -e '    tell application "Terminal"           ' """
        + """ -e """    + quotedCmd1
        + """ -e '        activate                          ' """
        + """ -e '    end tell                              ' """
        + """ -e 'else                                      ' """
        + """ -e '    tell application "Terminal"           ' """
        + """ -e """    + quotedCmd2
        + """ -e '        activate                          ' """
        + """ -e '    end tell                              ' """
        + """ -e 'end if                                    ' """
        )
    
    Popen(cmd_line, env=env, shell=True)

def load_plugin():
    from thonny.globals import get_workbench
    
    def open_system_shell_for_selected_interpreter(): 
        open_system_shell()
    
    get_workbench().add_command("OpenSystemShell", "tools", "Open system shell...",
                    open_system_shell_for_selected_interpreter,
                    tester=lambda: "system_shell" in get_runner().supported_features(),
                    group=80)
