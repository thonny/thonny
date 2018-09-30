"""
NB! The script should be runnable both with Python 2.7 and Python 3.*
Because some distros have only Python 2 installed (eg CentOS 7)
and some only Python 3 (eg latest Fedoras)
"""

from __future__ import print_function

import os.path
import shutil
import subprocess
import sys

if sys.version_info[0] == 2:
    input = raw_input  # @UndefinedVariable @ReservedAssignment


def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.
    (Copied from Python 3.5 shutil)
    """
    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return os.path.exists(fn) and os.access(fn, mode) and not os.path.isdir(fn)

    # If we're given a path with a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    if os.path.dirname(cmd):
        if _access_check(cmd, mode):
            return cmd
        return None

    if path is None:
        path = os.environ.get("PATH", os.defpath)
    if not path:
        return None
    path = path.split(os.pathsep)

    files = [cmd]

    seen = set()
    for dir_ in path:
        normdir = os.path.normcase(dir_)
        if not normdir in seen:
            seen.add(normdir)
            for thefile in files:
                name = os.path.join(dir_, thefile)
                if _access_check(name, mode):
                    return name
    return None


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
        if which(cmd):
            subprocess.call([cmd])
            break

    udd = "update-desktop-database"
    if which(udd):
        subprocess.call([udd, menu_dir])


if len(sys.argv) == 1:
    parent_dir = os.path.expanduser("~/apps")
elif len(sys.argv) == 2:
    parent_dir = os.path.abspath(os.path.expanduser(sys.argv[1].strip().rstrip("/")))
else:
    print("Installer should be run with 0 or 1 arguments", file=sys.stderr)
    exit(1)

if parent_dir.startswith(os.path.dirname(__file__)):
    print("Can't install into installer directory", file=sys.stderr)
    exit(1)


def print_task(desc):
    print((desc + " ").ljust(70, ".") + " ", end="")


def get_desktop_path():
    try:
        return subprocess.check_output(["xdg-user-dir", "DESKTOP"]).strip().decode()
    except:
        return os.path.expanduser("~/Desktop")


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
        answer = input(
            target_dir + " already exists. I need to clear it. Is it OK? [Y/n]: "
        ).strip()
        if not answer or answer.lower() in ["y", "yes"]:
            shutil.rmtree(target_dir)
        else:
            print("Installation is cancelled", file=sys.stderr)
            exit(1)

    shutil.copytree(source_dir, target_dir)  # Copy everything
    shutil.rmtree(target_dir + "/templates")  # ... except templates
    os.remove(target_dir + "/install")  # ... and installer
    print("Done!")

    menu_item_path = menu_dir + "/Thonny.desktop"
    print_task("Creating start menu item (%s)" % menu_item_path)
    create_launcher(
        source_dir + "/templates/Thonny.desktop",
        menu_item_path,
        {"$target_dir": target_dir},
    )
    print("Done!")

    print_task("Creating Desktop shortcut")
    desktop_path = get_desktop_path()

    create_launcher(
        source_dir + "/templates/Thonny.desktop",
        desktop_path + "/Thonny.desktop",
        {"$target_dir": target_dir},
    )
    print("Done!")

    uninstaller_path = target_dir + "/bin/uninstall"
    print_task("Creating uninstaller (%s)" % uninstaller_path)
    create_launcher(
        source_dir + "/templates/uninstall.sh",
        uninstaller_path,
        {"$target_dir": target_dir, "$menu_dir": menu_dir},
    )
    print("Done!")

    print_task("Compiling Python files")
    return_code = subprocess.call(
        [target_dir + "/bin/python3.7", "-m", "compileall", target_dir + "/lib"]
    )
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
