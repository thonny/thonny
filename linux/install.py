#!/usr/bin/env python3

# It doesn't matter which python3 is used for running this installation script,
# as Thonny installation is not interfering with any specific Python version,
# Python path won't be modified.

import sys
import os.path
import shutil

def replace_prefix_and_save_launcher(source_filename, target_filename):
    with open(source_filename) as f:
        content = f.read()

    target_dir = os.path.dirname(target_filename) 
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    with open(target_filename, mode="w") as f:
        f.write(content.replace("$prefix", prefix))
    
    # Seems that even desktop files have to be executable 
    # https://help.ubuntu.com/community/UnityLaunchersAndDesktopFiles
    os.chmod(target_filename, 0o755)
    

if len(sys.argv) == 2:
    prefix = os.path.expanduser(sys.argv[1].strip().rstrip("/"))
else:
    print("""Installer should be run with argument indicating the part of filesystem  
where Thonny should live. 

Usage examples for single user install:

    ./install ~/.local
    ./install /home/john/my_local_applications

Usage examples for systemwide install:

    sudo ./install /usr
    sudo ./install /usr/local
""")
    exit(1)
    

source_main_dir     = os.path.dirname(os.path.realpath(__file__))
target_main_dir     = prefix + "/lib/thonny"
target_script_path  = prefix + "/bin/thonny"
if prefix.startswith("/home"):
    target_menu_dir = os.path.expanduser("~/.local/share/applications")
else:
    target_menu_dir = "/usr/share/applications" 


if os.path.exists(target_main_dir):
    answer = input(target_main_dir + " already exists, may I clear it before installing this version [Y/n]: ").strip()
    if not answer or answer.lower() == "y":
        shutil.rmtree(target_main_dir)

print("Copying files to " + target_main_dir + " ... ", end="")
shutil.copytree(source_main_dir + "/thonny", target_main_dir + "/thonny")
print("Done!")


print("Creating executable " + target_script_path + " ... ", end="")
replace_prefix_and_save_launcher(source_main_dir + "/thonny.sh", target_script_path)
print("Done!")


print("Creating start menu item ... ", end="")
replace_prefix_and_save_launcher(source_main_dir + "/Thonny.desktop",
                                 target_menu_dir + "/Thonny.desktop")
print("Done!")


print("Creating desktop icon ... ", end="")
replace_prefix_and_save_launcher(source_main_dir + "/Thonny.desktop",
                                 os.path.expanduser("~/Desktop/Thonny.desktop"))
print("Done!")

print()
print("Installation was successful, you can start Thonny from start menu or desktop")
print()

