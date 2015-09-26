import sys
import os.path
from cx_Freeze import setup, Executable


MAIN_DIR = os.path.abspath("../..")

print(os.getcwd())
# Options shared by both Executables
build_exe_options = {
    'path' : [MAIN_DIR] + sys.path,
    'include_files': [MAIN_DIR + "/res",
                      MAIN_DIR + "/VERSION"],
    'packages': ["jedi", "rope", "turtle", "idlelib", "thonny"],
    'include_msvcr' : True, 
    'base' : "Win32GUI" if sys.platform == "win32" else None,
}

frontend_exe = Executable (
    script= MAIN_DIR + "/thonny_frontend.py",
    icon=MAIN_DIR + "/res/thonny.ico",
)

backend_exe = Executable (
    script=MAIN_DIR + "/thonny_backend.py",
)

with open(MAIN_DIR + "/VERSION") as vf:
    version = vf.read().strip()

setup (
    name = "thonny",
    version = version,
    description = "Thonny",
    executables = [frontend_exe, backend_exe],
    options = {'build_exe': build_exe_options}
)