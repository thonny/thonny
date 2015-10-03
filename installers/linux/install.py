#!/usr/bin/env python3

# It doesn't matter which python3 is used for running this installation script,
# as Thonny installation is not interfering with any specific Python version,
# Python path won't be modified.

import sys
import os.path
import shutil
import subprocess

def create_launcher(source_filename, target_filename, replacements={}):
    target_dir = os.path.dirname(target_filename) 
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    with open(source_filename) as f:
        content = f.read()

    with open(target_filename, mode="w") as f:
        for from_str in replacements:
            to_str = replacements[from_str]
            content = content.replace(from_str, to_str)
        f.write(content)
    
    # Seems that even desktop files have to be executable 
    # https://help.ubuntu.com/community/UnityLaunchersAndDesktopFiles
    os.chmod(target_filename, 0o755)
    

if len(sys.argv) == 1:
    parent_dir = "/opt"
elif len(sys.argv) == 2:
    parent_dir = os.path.expanduser(sys.argv[1].strip().rstrip("/"))
else:
    print("Installer should be run with 0 or 1 arguments", file=sys.stderr)
    exit(1)

def python_has_required_modules(python_command):
    try:
        result = subprocess.call(python_command + ' -c "import tkinter;import idlelib"', shell=True)
        return result == 0
    except:
        return False

def print_task(desc):
    print((desc + " ").ljust(70, ".") + " ", end="")


# Find suitable Python version
print_task("Checking available Python versions")
if python_has_required_modules("python3.4"):
    print("Done!")
    print("Thonny will use Python 3.4")
    python = "python3.4"
elif python_has_required_modules("python3.5"):
    print("Done!")
    print("Thonny will use Python 3.5")
    python = "python3.5"
else:
    print("Error!")
    if shutil.which("python3.4"):
        print("Python 3.4 exists, but misses tkinter or idlelib", file=sys.stderr)
    elif shutil.which("python3.5"):
        print("Python 3.5 exists, but misses tkinter or idlelib", file=sys.stderr)
    else:
        print("Can't find neither python3.4 nor python3.5", file=sys.stderr)
    exit(1)

# define directories    
source_dir = os.path.dirname(os.path.realpath(__file__))
target_dir = parent_dir + "/thonny"
if target_dir.startswith("/home"):
    menu_dir = os.path.expanduser("~/.local/share/applications")
else:
    menu_dir = "/usr/share/applications" 

try:
    # handle reinstalling newer version
    print_task("Copying files to " + target_dir)
    
    if os.path.exists(target_dir):
        print()
        answer = input(target_dir + " already exists. I need to clear it. Is it OK? [Y/n]: ").strip()
        if not answer or answer.lower() == "y":
            shutil.rmtree(target_dir)
        else:
            print("Installation is cancelled", file=sys.stderr)
            exit(1)
    
    shutil.copytree(source_dir + "/share", target_dir + "/share")
    shutil.copy(source_dir + "/license.txt", target_dir + "/license.txt")
    os.makedirs(target_dir + "/bin")
    exe_path = target_dir + "/bin/thonny"
    create_launcher(source_dir + "/templates/thonny.sh",
                    exe_path,
                    {"$target_dir" : target_dir, "$python" : python})
    print("Done!")
    
    
    menu_item_path = menu_dir + "/Thonny.desktop"
    print_task("Creating start menu item (%s)" % menu_item_path)
    create_launcher(source_dir + "/templates/Thonny.desktop",
                    menu_item_path,
                    {"$target_dir" : target_dir})
    print("Done!")
    
    
    uninstaller_path = target_dir + "/bin/uninstall"
    print_task("Creating uninstaller (%s)" % uninstaller_path)
    create_launcher(source_dir + "/templates/uninstall.sh",
                    uninstaller_path,
                    {"$target_dir" : target_dir, "$menu_dir" : menu_dir})
    print("Done!")
    
    
    print()
    print("Installation was successful, you can start Thonny from start menu under")
    print("Education or Programming, or by calling " + exe_path)
    
    print()
    
except PermissionError as e:
    print()
    print(e, file=sys.stderr)
    exit(1)
    
