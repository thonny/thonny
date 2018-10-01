"""Prints information about how should one run python or pip so that the commands
affect same Python installation that is used for running this script"""

import os.path
import platform
import subprocess
import sys
from shutil import which


def _find_commands(logical_command, reference_output, query_arguments, only_best=True):
    """Returns the commands that can be used for running given conceptual command
    (python or pip)"""

    def is_correct_command(command):
        # Don't try to run the command itself, but first expand it to full path.
        # The location of parent executable seems to affect command search.
        full_path = which(command)
        if full_path is None:
            return False

        try:
            output = subprocess.check_output(
                [full_path] + query_arguments, universal_newlines=True, shell=False
            )

            expected = reference_output.strip()
            actual = output.strip()
            if platform.system() == "Windows":
                expected = expected.lower()
                actual = actual.lower()

            return expected in actual
        except Exception:
            return False

    correct_commands = set()

    # first look for short commands
    for suffix in _get_version_suffixes():
        command_ = logical_command + suffix
        if is_correct_command(command_):
            if " " in command_:
                command_ = '"' + command_ + '"'

            correct_commands.add(command_)
            if only_best:
                return list(correct_commands)

    # if no Python found, then use executable
    if (
        len(correct_commands) == 0
        and logical_command == "python"
        and platform.system() != "Windows"
    ):  # Unixes tend to use symlinks, not Windows
        correct_commands.add(sys.executable)
        if only_best:
            return list(correct_commands)

    # if still nothing found, then add full paths
    if len(correct_commands) == 0:
        if platform.system() == "Windows":
            exe_suffix = ".exe"
        else:
            exe_suffix = ""

        folders = [
            sys.exec_prefix,
            os.path.join(sys.exec_prefix, "bin"),
            os.path.join(sys.exec_prefix, "Scripts"),
        ]

        for suffix in _get_version_suffixes():
            command_ = logical_command + suffix
            for folder in folders:
                full_command = os.path.join(folder, command_)
                if os.path.exists(full_command + exe_suffix):
                    if " " in full_command:
                        full_command = '"' + full_command + '"'

                    correct_commands.add(full_command)
                    if only_best:
                        return list(correct_commands)

    return sorted(correct_commands, key=len)


def _find_python_commands(only_best=True):
    return _find_commands(
        "python",
        sys.exec_prefix + "\n" + sys.version,
        ["-c", "import sys; print(sys.exec_prefix); print(sys.version)"],
        only_best,
    )


def _find_pip_commands(only_best=True):
    # Asking pip version is quite slow.
    # Trying a shortcut for common case:
    #  if $(which <command>) lives in the same dir as current interpreter
    #  and we're using Thonny-private venv,
    #  we can trust the command is the right one.
    pref_cmd = "pip" + _get_version_suffixes()[0]
    pref_cmd_path = which(pref_cmd)
    if pref_cmd_path:
        pref_cmd_dir = os.path.dirname(pref_cmd_path)
        current_exe_dir = os.path.dirname(sys.executable)
        if pref_cmd_dir == current_exe_dir and os.path.isfile(
            os.path.join(current_exe_dir, "is_private")
        ):
            return [pref_cmd]

    # Fallback
    current_ver_string = _get_pip_version_string()

    if current_ver_string is not None:
        commands = _find_commands("pip", current_ver_string, ["--version"], only_best)
        if len(commands) > 0:
            return commands
        else:
            python_commands = _find_python_commands(True)
            return [python_commands[0] + " -m pip"]
    else:
        return []


def _get_version_suffixes():
    major = str(sys.version_info.major)
    minor = "%d.%d" % (sys.version_info.major, sys.version_info.minor)

    if platform.system() == "Windows":
        return ["", major, minor]
    else:
        return [major, minor, ""]


def _get_pip_version_string():
    try:
        import pip
        return os.path.dirname(pip.__file__)
    except ImportError:
        return None


def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    _clear_screen()
    print("*" * 80)
    print(
        "This session is prepared for using Python %s installation in"
        % platform.python_version()
    )
    print(" ", sys.exec_prefix)
    print("")
    print("Command for running the interpreter:")
    for py_command in _find_python_commands(True):
        print(" ", py_command)

    print("")
    print("Command for running pip:")
    # print(_get_pip_version_string())
    pip_commands = _find_pip_commands(True)
    if len(pip_commands) == 0:
        print(" ", "<pip is not installed>")
    else:
        for pip_command in pip_commands:
            print(" ", pip_command)

    print("")
    print("*" * 80)
