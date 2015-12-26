"""Prints information about how should one run python or pip so that the commands
affect same Python installation that is used for running this script"""

import os.path
import sys
import platform
import subprocess
from shutil import which

def create_pythonless_environment():
    # If I want to call another python version, then 
    # I need to remove from environment the items installed by current interpreter
    env = {}
    
    for key in os.environ:
        if ("python" not in key.lower()
            and key not in ["TK_LIBRARY", "TCL_LIBRARY"]):
            env[key] = os.environ[key]
    
    return env

def _find_commands(logical_command, reference_output, query_arguments,
                   only_shortest=True):
    """Returns the commands that can be used for running given conceptual command
    (python or pip)"""
    
    def is_correct_command(command):
        # Don't try to run the command itself, but first expand it to full path.
        # The location of parent executable seems to affect command search.
        full_path = which(command)
        if full_path is None:
            return False

            
        try:
            output = subprocess.check_output([full_path] + query_arguments, 
                                             universal_newlines=True,
                                             shell=False,
                                             env=create_pythonless_environment())
            
            expected = reference_output.strip()
            actual = output.strip()
            if platform.system() == "Windows":
                expected = expected.lower()
                actual = actual.lower()
                
            return expected == actual
        except:
            return False
    
    correct_commands = set()
    version_suffixes = ["",
                   str(sys.version_info.major),
                   "%d.%d" % (sys.version_info.major, sys.version_info.minor)
                   ]
    
    # first look for short commands
    for suffix in version_suffixes:
        command = logical_command + suffix
        if is_correct_command(command):
            if " " in command:
                command = '"' + command + '"'
                
            correct_commands.add(command)
            if only_shortest:
                return list(correct_commands)
    
    # if no Python found, then use executable
    if (len(correct_commands) == 0
        and logical_command == "python" 
        and platform.system() != "Windows"): # Unixes tend to use symlinks, not Windows
        correct_commands.add(sys.executable)
        if only_shortest:
            return list(correct_commands)
    
    # if still nothing found, then add full paths
    if len(correct_commands) == 0:
        if platform.system() == "Windows":
            exe_suffix = ".exe"
        else:
            exe_suffix = ""
            
        folders = [sys.exec_prefix, 
                   os.path.join(sys.exec_prefix, "bin"),
                   os.path.join(sys.exec_prefix, "Scripts")]
        
        for suffix in version_suffixes:
            command = logical_command + suffix
            for folder in folders:
                full_command = os.path.join(folder, command)
                if os.path.exists(full_command + exe_suffix):
                    if " " in full_command:
                        full_command = '"' + full_command + '"'
                        
                    correct_commands.add(full_command)
                    if only_shortest:
                        return list(correct_commands)
    
    return sorted(correct_commands, key=lambda x: len(x))

def _find_python_commands(only_shortest=True):
    return _find_commands("python",
                         sys.exec_prefix + "\n" + sys.version,
                         ["-c", "import sys; print(sys.exec_prefix); print(sys.version)"], only_shortest)

def _find_pip_commands(only_shortest=True):
    current_ver_string = _get_pip_version_string()
    
    if current_ver_string is not None:
        commands = _find_commands("pip", current_ver_string, ["--version"], only_shortest)
        if len(commands) > 0:
            return commands
        else:
            python_commands = _find_python_commands(True)
            return [python_commands[0] + " -m pip"]
    else:
        return []
    


def _get_pip_version_string():
    import io
    try:
        import pip
    except ImportError:
        return None
    
    # capture output
    original_stdout = sys.stdout 
    try:
        sys.stdout = io.StringIO()
        try:
            pip.main(["--version"])
        except SystemExit:
            pass
        return sys.stdout.getvalue().strip()
    finally:
        sys.stdout = original_stdout


def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    _clear_screen()
    print("*" * 80)
    print("This session is prepared for using Python %s installation in" % platform.python_version())
    print(" ", sys.exec_prefix)
    print("")
    print("Shortest command for running the interpreter:")
    for command in _find_python_commands(True):
        print(" ", command)
        
    print("")
    print("Shortest command for running pip:")
    #print(_get_pip_version_string())
    pip_commands = _find_pip_commands(True)
    if len(pip_commands) == 0:
        print(" ", "<pip is not installed>")
    else:
        for command in pip_commands:
            print(" ", command)
    
    print("")
    print("*" * 80)
    