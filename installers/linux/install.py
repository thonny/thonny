#!/usr/bin/env python3

# It doesn't matter which python3 is used for running this installation script,
# as Thonny installation is not interfering with any specific Python version,
# Python path won't be modified.

import sys
import os.path
import shutil
import subprocess

def create_launcher(source_filename, target_filename, replacements={}):
    with open(source_filename) as f:
        content = f.read()

    target_dir = os.path.dirname(target_filename) 
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    with open(target_filename, mode="w") as f:
        for from_str in replacements:
            to_str = replacements[from_str]
            content = content.replace(to_str, from_str)
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
        return subprocess.call(python_command + ' -c "import idlelib"') == 0
    except:
        return False


# Find suitable Python version
print("Checking available Python versions ... ", end="")
if python_has_required_modules("python3.4"):
    print("Done! Thonny will use Python 3.4")
    python = "python3.4"
elif python_has_required_modules("python3.5"):
    print("Done! Thonny will use Python 3.5")
    python = "python3.5"
else:
    print("Error!")
    if shutil.which("python3.4"):
        print("Python 3.4 exists, but misses 'idlelib'", file=sys.stderr)
    elif shutil.which("python3.5"):
        print("Python 3.5 exists, but misses 'idlelib'", file=sys.stderr)
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


# handle reinstalling newer version
if os.path.exists(target_dir):
    answer = input(target_dir + " already exists, may I clear it before installing this version [Y/n]: ").strip()
    if not answer or answer.lower() == "y":
        shutil.rmtree(target_dir)

print("Copying files to " + target_dir + " ... ", end="")
shutil.copytree(source_dir + "/share", target_dir + "/share")
shutil.copy(source_dir + "/LICENSE", source_dir + "/LICENSE")
exe_path = target_dir + "/bin/thonny"
create_launcher(source_dir + "/thonny.sh",
                exe_path,
                {"$target_dir" : target_dir, "$python" : python})
print("Done!")


menu_item_path = menu_dir + "/Thonny.desktop"
print("Creating start menu item (%s) ... " % menu_item_path, end="")
create_launcher(source_dir + "/Thonny.desktop",
                menu_item_path,
                {"$target_dir" : target_dir})
print("Done!")


uninstaller_path = target_dir + "/bin/uninstall"
print("Creating uninstaller (%s) ... " % uninstaller_path, end="")
create_launcher(source_dir + "/uninstall.sh",
                uninstaller_path,
                {"$target_dir" : target_dir, "$menu_dir" : menu_dir})
print("Done!")


print()
print("Installation was successful, you can start Thonny from start menu")
print("or by calling " + exe_path)

print()

