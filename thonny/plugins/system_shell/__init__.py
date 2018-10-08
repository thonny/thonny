# -*- coding: utf-8 -*-
import os.path
import platform
import shlex
import shutil
import subprocess
from subprocess import Popen, check_output
from time import sleep
from tkinter.messagebox import showerror

from thonny import THONNY_USER_DIR, get_runner, get_workbench
from thonny.common import normpath_with_actual_case
from thonny.running import create_pythonless_environment


def _get_exec_prefix(python_interpreter):

    return check_output(
        [python_interpreter, "-c", "import sys; print(sys.exec_prefix)"],
        universal_newlines=True,
        env=create_pythonless_environment(),
    ).strip()


def _add_to_path(directory, path):
    # Always prepending to path may seem better, but this could mess up other things.
    # If the directory contains only one Python distribution executables, then
    # it probably won't be in path yet and therefore will be prepended.
    if (
        directory in path.split(os.pathsep)
        or platform.system() == "Windows"
        and directory.lower() in path.lower().split(os.pathsep)
    ):
        return path
    else:
        return directory + os.pathsep + path


def open_system_shell():
    """Main task is to modify path and open terminal window.
    Bonus (and most difficult) part is executing a script in this window
    for recommending commands for running given python and related pip"""
    python_interpreter = get_runner().get_executable()
    if python_interpreter is None:
        return None

    exec_prefix = _get_exec_prefix(python_interpreter)
    if ".." in exec_prefix:
        exec_prefix = normpath_with_actual_case(exec_prefix)
    env = create_pythonless_environment()

    # TODO: take care of SSL_CERT_FILE (unset when running external python and set for builtin)
    # Unset when we're in builtin python and target python is external

    # TODO: what if executable or explainer needs escaping?
    # Maybe try creating a script in temp folder and execute this,
    # passing required paths via environment variables.

    interpreter = python_interpreter.replace("pythonw", "python")
    explainer = os.path.join(os.path.dirname(__file__), "explain_environment.py")
    cwd = get_workbench().get_cwd()

    if platform.system() == "Windows":
        return _open_shell_in_windows(cwd, env, interpreter, explainer, exec_prefix)

    elif platform.system() == "Linux":
        return _open_shell_in_linux(cwd, env, interpreter, explainer, exec_prefix)

    elif platform.system() == "Darwin":
        _open_shell_in_macos(cwd, env, interpreter, explainer, exec_prefix)
    else:
        showerror(
            "Problem",
            "Don't know how to open system shell on this platform (%s)" % platform.system(),
            parent=get_workbench()
        )

    return None


def _open_shell_in_windows(cwd, env, interpreter, explainer, exec_prefix):
    env["PATH"] = _add_to_path(exec_prefix + os.pathsep, env.get("PATH", ""))
    env["PATH"] = _add_to_path(
        os.path.join(exec_prefix, "Scripts"), env.get("PATH", "")
    )

    # Yes, the /K argument has weird quoting. Can't explain this, but it works
    cmd_line = """start "Shell for {interpreter}" /D "{cwd}" /W cmd /K ""{interpreter}" "{explainer}"" """.format(
        interpreter=interpreter, cwd=cwd, explainer=explainer
    )

    Popen(cmd_line, env=env, shell=True)


def _open_shell_in_linux(cwd, env, interpreter, explainer, exec_prefix):
    def _shellquote(s):
        return subprocess.list2cmdline([s])

    # No escaping in PATH possible: http://stackoverflow.com/a/29213487/261181
    # (neither necessary except for colon)
    env["PATH"] = _add_to_path(os.path.join(exec_prefix, "bin"), env["PATH"])

    xte = shutil.which("x-terminal-emulator")
    if xte:
        if (os.path.realpath(xte).endswith("/lxterminal")
            and shutil.which("lxterminal")):
            # need to know, see below
            term_cmd = "lxterminal"
        else:
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
    elif shutil.which("xfce4-terminal"):
        term_cmd = "xfce4-terminal"
    elif shutil.which("lxterminal"):
        term_cmd = "lxterminal"
    elif shutil.which("xterm"):
        term_cmd = "xterm"
    else:
        raise RuntimeError("Don't know how to open terminal emulator")

    # Need to prevent shell from closing after executing the command:
    # http://stackoverflow.com/a/4466566/261181
    core_cmd = "{interpreter} {explainer}; exec bash -i".format(
        interpreter=_shellquote(interpreter), explainer=_shellquote(explainer)
    )
    in_term_cmd = "bash -c {core_cmd}".format(core_cmd=_shellquote(core_cmd))
    
    if term_cmd == "lxterminal":
        # https://www.raspberrypi.org/forums/viewtopic.php?t=221490
        whole_cmd = "{term_cmd} --command={in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd)
        )
    else:
        whole_cmd = "{term_cmd} -e {in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd)
        )
        

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
    cmd = "PATH={}; unset TK_LIBRARY; unset TCL_LIBRARY".format(
        _shellquote(env["PATH"])
    )

    if "SSL_CERT_FILE" in env:
        cmd += ";export SSL_CERT_FILE=" + _shellquote(env["SSL_CERT_FILE"])

    cmd += "; {interpreter} {explainer}".format(
        interpreter=_shellquote(interpreter), explainer=_shellquote(explainer)
    )

    # The script will be sent to Terminal with 'do script' command, which takes a string.
    # We'll prepare an AppleScript string literal for this
    # (http://stackoverflow.com/questions/10667800/using-quotes-in-a-applescript-string):
    cmd_as_apple_script_string_literal = (
        '"' + cmd.replace("\\", "\\\\").replace('"', '\\"') + '"'
    )

    # When Terminal is not open, then do script opens two windows.
    # do script ... in window 1 would solve this, but if Terminal is already
    # open, this could run the script in existing terminal (in undesirable env on situation)
    # That's why I need to prepare two variations of the 'do script' command
    doScriptCmd1 = """        do script %s """ % cmd_as_apple_script_string_literal
    doScriptCmd2 = (
        """        do script %s in window 1 """ % cmd_as_apple_script_string_literal
    )

    # The whole AppleScript will be executed with osascript by giving script
    # lines as arguments. The lines containing our script need to be shell-quoted:
    quotedCmd1 = subprocess.list2cmdline([doScriptCmd1])
    quotedCmd2 = subprocess.list2cmdline([doScriptCmd2])

    # Now we can finally assemble the osascript command line
    cmd_line = (
        "osascript"
        + """ -e 'if application "Terminal" is running then ' """
        + """ -e '    tell application "Terminal"           ' """
        + """ -e """
        + quotedCmd1
        + """ -e '        activate                          ' """
        + """ -e '    end tell                              ' """
        + """ -e 'else                                      ' """
        + """ -e '    tell application "Terminal"           ' """
        + """ -e """
        + quotedCmd2
        + """ -e '        activate                          ' """
        + """ -e '    end tell                              ' """
        + """ -e 'end if                                    ' """
    )

    Popen(cmd_line, env=env, shell=True)


def load_plugin() -> None:
    def open_system_shell_for_selected_interpreter():
        open_system_shell()

    get_workbench().add_command(
        "OpenSystemShell",
        "tools",
        "Open system shell...",
        open_system_shell_for_selected_interpreter,
        tester=lambda: "system_shell" in get_runner().supported_features(),
        group=80,
    )
