import sys
import os.path
from cx_Freeze import setup, Executable
import shutil


MAIN_DIR = os.path.abspath("../..")

# make sure backend_private is up to date ------------------------
bp_path = os.path.join(MAIN_DIR, "backend_private")
os.makedirs(bp_path, 0o777, True)
os.makedirs(os.path.join(bp_path, "thonny"), 0o777, True)

for filename in ["thonny_backend.py",
                 os.path.join("thonny", "backend.py"),
                 os.path.join("thonny", "ast_utils.py"),
                 os.path.join("thonny", "misc_utils.py"),
                 os.path.join("thonny", "common.py")]:
    original = os.path.join(MAIN_DIR, filename)
    copy = os.path.join(bp_path, filename)
    
    if os.path.exists(original): 
        shutil.copyfile(original, copy)
        


# Options shared by both Executables ----------------------------
build_exe_options = {
    'path' : [MAIN_DIR] + sys.path,
    'include_files': [os.path.join(MAIN_DIR, "res"),
                      os.path.join(MAIN_DIR , "VERSION"),
                      os.path.join(MAIN_DIR, "backend_private")],
    'packages': ["jedi", "rope", "turtle", "idlelib", "thonny"],
    'include_msvcr' : True, 
    'base' : "Win32GUI" if sys.platform == "win32" else None,
}

frontend_exe = Executable (
    script = os.path.join(MAIN_DIR, "thonny_frontend.py"),
    icon = os.path.join(MAIN_DIR, "res", "thonny.ico"),
)

backend_exe = Executable (
    script = os.path.join(MAIN_DIR, "thonny_backend.py"),
)

with open(os.path.join(MAIN_DIR, "VERSION")) as vf:
    version = vf.read().strip()

setup (
    name = "thonny",
    version = version,
    description = "Thonny",
    executables = [frontend_exe, backend_exe],
    options = {'build_exe': build_exe_options}
)