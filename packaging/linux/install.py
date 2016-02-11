#!/usr/bin/env python

from __future__ import print_function

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
    
def try_to_refresh_desktop_and_menus(menu_dir):
    """In KDE, the .destop files are not taken into account immediately"""
    for cmd in ["kbuildsycoca5", "kbuildsycoca4", "kbuildsycoca"]:
        if shutil.which(cmd):
            subprocess.call([cmd])
            break
    
    udd = "update-desktop-database"
    if shutil.which(udd):
        subprocess.call([udd, menu_dir])
        

if len(sys.argv) == 1:
    parent_dir = os.path.expanduser("~/apps")
elif len(sys.argv) == 2:
    parent_dir = os.path.expanduser(sys.argv[1].strip().rstrip("/"))
else:
    print("Installer should be run with 0 or 1 arguments", file=sys.stderr)
    exit(1)

def print_task(desc):
    print((desc + " ").ljust(70, ".") + " ", end="")


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
        answer = raw_input(target_dir + " already exists. I need to clear it. Is it OK? [Y/n]: ").strip()
        if not answer or answer.lower() == "y":
            shutil.rmtree(target_dir)
        else:
            print("Installation is cancelled", file=sys.stderr)
            exit(1)
    
    shutil.copytree(source_dir, target_dir)  # Copy everything
    shutil.rmtree(target_dir + "/templates") # ... except templates
    os.remove(target_dir + "/install")       # ... and installer
    print("Done!")
    
    
    menu_item_path = menu_dir + "/Thonny.desktop"
    print_task("Creating start menu item (%s)" % menu_item_path)
    create_launcher(source_dir + "/templates/Thonny.desktop",
                    menu_item_path,
                    {"$target_dir" : target_dir})
    print("Done!")
    
    print_task("Creating Desktop shortcut")
    create_launcher(source_dir + "/templates/Thonny.desktop",
                    os.path.expanduser("~/Desktop/Thonny.desktop"),
                    {"$target_dir" : target_dir})
    print("Done!")
    
    
    uninstaller_path = target_dir + "/bin/uninstall"
    print_task("Creating uninstaller (%s)" % uninstaller_path)
    create_launcher(source_dir + "/templates/uninstall.sh",
                    uninstaller_path,
                    {"$target_dir" : target_dir, "$menu_dir" : menu_dir})
    print("Done!")
    
    print_task("Compiling Python files")
    return_code = subprocess.call([target_dir + "/bin/python3.5",
                           "-m", "compileall", target_dir + "/lib"])
    # TODO: why is return code 1 (eg. in 64-bit Fedora 22) even when everything seemed to succeed?
    print("Done!")
    
    print_task("Refreshing system menu")
    try_to_refresh_desktop_and_menus(menu_dir)
    print("Done!")
    
    
    print()
    print("Installation was successful, you can start Thonny from start menu under")
    print("Education or Programming, or by calling " + target_dir + "/bin/thonny")
    print("For uninstalling Thonny call " + target_dir + "/bin/uninstall")
    
    
except OSError as e:
    print()
    print(e, file=sys.stderr)
    exit(1)
    
