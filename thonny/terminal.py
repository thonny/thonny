import os.path
import platform
import shlex
import subprocess
import sys


def run_in_terminal(cmd, cwd, env_overrides={}, keep_open=True, title=None):
    from thonny.running import get_environment_with_overrides

    env = get_environment_with_overrides(env_overrides)

    if not cwd or not os.path.exists(cwd):
        cwd = os.getcwd()

    if platform.system() == "Windows":
        _run_in_terminal_in_windows(cmd, cwd, env, keep_open, title)
    elif platform.system() == "Linux":
        _run_in_terminal_in_linux(cmd, cwd, env, keep_open)
    elif platform.system() == "Darwin":
        _run_in_terminal_in_macos(cmd, cwd, env_overrides, keep_open)
    else:
        raise RuntimeError("Can't launch terminal in " + platform.system())


def open_system_shell(cwd, env_overrides={}):
    from thonny.running import get_environment_with_overrides

    env = get_environment_with_overrides(env_overrides)

    if platform.system() == "Darwin":
        _run_in_terminal_in_macos([], cwd, env_overrides, True)
    elif platform.system() == "Windows":
        cmd = "start cmd"
        subprocess.Popen(cmd, cwd=cwd, env=env, shell=True)
    elif platform.system() == "Linux":
        cmd = _get_linux_terminal_command()
        subprocess.Popen(cmd, cwd=cwd, env=env, shell=True)
    else:
        raise RuntimeError("Can't launch terminal in " + platform.system())


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


def _run_in_terminal_in_windows(cmd, cwd, env, keep_open, title=None):
    if keep_open:
        # Yes, the /K argument has weird quoting. Can't explain this, but it works
        quoted_args = " ".join(map(lambda s: s if s == "&" else '"' + s + '"', cmd))
        cmd_line = """start {title} /D "{cwd}" /W cmd /K "{quoted_args}" """.format(
            cwd=cwd, quoted_args=quoted_args, title='"' + title + '"' if title else ""
        )

        subprocess.Popen(cmd_line, cwd=cwd, env=env, shell=True)
    else:
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=cwd, env=env)


def _run_in_terminal_in_linux(cmd, cwd, env, keep_open):
    def _shellquote(s):
        return subprocess.list2cmdline([s])

    term_cmd = _get_linux_terminal_command()

    if isinstance(cmd, list):
        cmd = " ".join(map(_shellquote, cmd))

    if keep_open:
        # http://stackoverflow.com/a/4466566/261181
        core_cmd = "{cmd}; exec bash -i".format(cmd=cmd)
        in_term_cmd = "bash -c {core_cmd}".format(core_cmd=_shellquote(core_cmd))
    else:
        in_term_cmd = cmd

    if term_cmd == "lxterminal":
        # https://www.raspberrypi.org/forums/viewtopic.php?t=221490
        whole_cmd = "{term_cmd} --command={in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd)
        )
    else:
        whole_cmd = "{term_cmd} -e {in_term_cmd}".format(
            term_cmd=term_cmd, in_term_cmd=_shellquote(in_term_cmd)
        )

    if term_cmd == "terminator" and "PYTHONPATH" in env:
        # it is written in Python 2 and the PYTHONPATH of Python 3 will confuse it
        # https://github.com/thonny/thonny/issues/1129
        del env["PYTHONPATH"]

    subprocess.Popen(whole_cmd, cwd=cwd, env=env, shell=True)


def _run_in_terminal_in_macos(cmd, cwd, env_overrides, keep_open):
    _shellquote = shlex.quote

    cmds = "clear; cd " + _shellquote(cwd)
    # osascript "tell application" won't change Terminal's env
    # (at least when Terminal is already active)
    # At the moment I just explicitly set some important variables
    for key in env_overrides:
        if env_overrides[key] is None:
            cmds += "; unset " + key
        else:
            value = env_overrides[key]
            if key == "PATH":
                value = _normalize_path(value)

            cmds += "; export {key}={value}".format(key=key, value=_shellquote(value))

    if cmd:
        if isinstance(cmd, list):
            cmd = " ".join(map(_shellquote, cmd))
        cmds += "; " + cmd

    if not keep_open:
        cmds += "; exit"

    # try to shorten to avoid too long line https://github.com/thonny/thonny/issues/1529

    common_prefix = os.path.normpath(sys.prefix).rstrip("/")
    cmds = (
        "export THOPR=" + common_prefix + " ; " + cmds.replace(common_prefix + "/", "$THOPR" + "/")
    )
    print(cmds)

    # The script will be sent to Terminal with 'do script' command, which takes a string.
    # We'll prepare an AppleScript string literal for this
    # (http://stackoverflow.com/questions/10667800/using-quotes-in-a-applescript-string):
    cmd_as_apple_script_string_literal = (
        '"' + cmds.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'
    )

    # When Terminal is not open, then do script opens two windows.
    # do script ... in window 1 would solve this, but if Terminal is already
    # open, this could run the script in existing terminal (in undesirable env on situation)
    # That's why I need to prepare two variations of the 'do script' command
    doScriptCmd1 = """        do script %s """ % cmd_as_apple_script_string_literal
    doScriptCmd2 = """        do script %s in window 1 """ % cmd_as_apple_script_string_literal

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

    subprocess.Popen(cmd_line, cwd=cwd, shell=True)


def _get_linux_terminal_command():
    import shutil

    xte = shutil.which("x-terminal-emulator")
    if xte:
        if os.path.realpath(xte).endswith("/lxterminal") and shutil.which("lxterminal"):
            # need to know exact program, because it needs special treatment
            return "lxterminal"
        elif os.path.realpath(xte).endswith("/terminator") and shutil.which("terminator"):
            # https://github.com/thonny/thonny/issues/1129
            return "terminator"
        else:
            return "x-terminal-emulator"
    # Older konsole didn't pass on the environment
    elif shutil.which("konsole"):
        if (
            shutil.which("gnome-terminal")
            and "gnome" in os.environ.get("DESKTOP_SESSION", "").lower()
        ):
            return "gnome-terminal"
        else:
            return "konsole"
    elif shutil.which("gnome-terminal"):
        return "gnome-terminal"
    elif shutil.which("xfce4-terminal"):
        return "xfce4-terminal"
    elif shutil.which("lxterminal"):
        return "lxterminal"
    elif shutil.which("xterm"):
        return "xterm"
    else:
        raise RuntimeError("Don't know how to open terminal emulator")


def _normalize_path(s):
    parts = s.split(os.pathsep)
    return os.pathsep.join([os.path.normpath(part) for part in parts])
