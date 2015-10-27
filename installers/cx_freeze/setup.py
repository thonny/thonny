import sys
import os.path
from cx_Freeze import setup, Executable
import shutil
from pkgutil import iter_modules

def module_exists(module_name):
    return module_name in (name for loader, name, ispkg in iter_modules())

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
        

stdlib_packages = [
                 "string",
                 "difflib",
                 "textwrap",
                 "unicodedata",
                 "stringprep",
                 
                 "struct",
                 "codecs",
                 
                 "datetime",
                 "calendar",
                 "collections", # TODO: .abc ???
                 "heapq",
                 "bisect",
                 "array",
                 "weakref",
                 "types",
                 "copy",
                 "pprint",
                 "reprlib",
                 "enum",
                 
                 "numbers",
                 "math",
                 "cmath",
                 "decimal",
                 "fractions",
                 "random",
                 "statistics",
                 
                 "itertools",
                 "functools",
                 "operator",
                 
                 "pathlib",
                 #os", # TODO: os.path ??
                 "fileinput",
                 "stat",
                 "filecmp",
                 "tempfile",
                 "glob",
                 "fnmatch",
                 "linecache",
                 "shutil",
                 
                 "pickle",
                 "copyreg",
                 "shelve",
                 "marshal",
                 "dbm",
                 "sqlite3",
                 
                 "zlib",
                 "gzip",
                 "bz2",
                 "lzma",
                 "zipfile",
                 "tarfile",
                 
                 "csv",
                 "configparser",
                 "netrc",
                 "xdrlib",
                 "plistlib",
                 
                 "hashlib",
                 "hmac",
                 "os",
                 "io",
                 "time",
                 "argparse",
                 "getopt",
                 "logging", # TODO: config, handlers
                 "getpass",
                 #"curses", # not available in windows
                 "platform",
                 "errno",
                 "ctypes",
                 
                 "threading",
                 "multiprocessing",
                 "concurrent",
                 "subprocess",
                 "sched",
                 "queue",
                 "_thread",
                 
                 "socket",
                 "ssl",
                 "select",
                 "selectors",
                 "asyncio",
                 "asyncore",
                 "asynchat",
                 "signal",
                 "mmap",
                 
                 "email",
                 "json",
                 "mailcap",
                 "mailbox",
                 "mimetypes",
                 "base64",
                 "binhex",
                 "binascii",
                 "quopri",
                 "uu",
                 
                 "html",
                 "xml",
                 
                 "webbrowser",
                 "cgi",
                 "cgitb",
                 "wsgiref",
                 "urllib",
                 "http",
                 "ftplib",
                 "poplib",
                 "imaplib",
                 "nntplib",
                 "smtplib",
                 "smtpd",
                 "telnetlib",
                 "uuid",
                 "socketserver",
                 "xmlrpc",
                 "ipaddress",
                 
                 "audioop",
                 "aifc",
                 "sunau",
                 "wave",
                 "chunk",
                 "colorsys",
                 "imghdr",
                 "sndhdr",
                 
                 "gettext",
                 "locale",
                 
                 "turtle",
                 "cmd",
                 "shlex",
                 
                 "tkinter",
                 "idlelib", # TODO: does it cause warnings when I'm not using it?
                 
                 "pydoc",
                 "doctest",
                 "unittest",
                 #"test" # Meant only for Python devs
                 
                 "bdb",
                 "faulthandler",
                 "pdb",
                 "timeit",
                 "trace",
                 "tracemalloc",
                 
                 "distutils",
                 "ensurepip", # TODO: ???
                 "venv",
                 
                 "sys",
                 "sysconfig",
                 "builtins",
                 "warnings",
                 "contextlib",
                 "abc",
                 "atexit",
                 "traceback",
                 "gc",
                 "inspect",
                 "site",
                 #"fpectl", # not built by default
                 
                 "code",
                 "codeop",
                 
                 "zipimport",
                 "pkgutil",
                 "modulefinder",
                 "runpy",
                 "importlib",
                 
                 "parser",
                 "ast",
                 "symtable",
                 "symbol",
                 "token",
                 "keyword",
                 "tokenize",
                 "tabnanny",
                 "pyclbr",
                 "py_compile",
                 "compileall",
                 "dis",
                 "pickletools", # TODO: ???
                 
                 "formatter",
                 ####################################
                     "pyexpat",
                     "select",
                     "unicodedata",
                     "_bz2",
                     "_ctypes",
                     "_ctypes_test",
                     "_decimal",
                     "_elementtree",
                     "_hashlib",
                     "_lzma",
                     "_multiprocessing",
                     "_socket",
                     "_sqlite3",
                     "_ssl",
                     "_testbuffer",
                     "_testcapi",
                     "_testimportmultiple",
                     "_tkinter",
                 ]

platform_specific_or_hidden = [
                     "_msi",
                     "_overlapped",
                     "winsound",
                     "readline",
                     "rlcompleter",
                     "ossaudiodev",
                     ]

for module_name in platform_specific_or_hidden:
    if module_exists(module_name):        
        stdlib_packages.append(module_name)

extra_packages = ["pygame"]

packages = ["jedi", "rope", "thonny"] + stdlib_packages + extra_packages

# Options shared by both Executables ----------------------------
build_exe_options = {
    'path' : [MAIN_DIR] + sys.path,
    'include_files': [os.path.join(MAIN_DIR, "res"),
                      os.path.join(MAIN_DIR , "VERSION"),
                      os.path.join(MAIN_DIR, "backend_private")],
    'packages' : packages,
    'include_msvcr' : True, 
    'base' : "Win32GUI" if sys.platform == "win32" else None,
}

frontend_exe = Executable (
    script = os.path.join(MAIN_DIR, "thonny_frontend.py"),
    icon = os.path.join(MAIN_DIR, "res", "thonny.ico"),
)

backend_exe = Executable (
    script = os.path.join(MAIN_DIR, "thonny_backend_cx_freeze.py"),
    targetName = "thonny_backend" + (".exe" if sys.platform == "win32" else "")
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