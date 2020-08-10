import logging
import os

from thonny import get_runner
from thonny.assistance import ProgramAnalyzer, add_program_analyzer
from thonny.common import is_same_path

known_stdlib_modules = {
    # Compiled from https://docs.python.org/3.7/py-modindex.html
    "__future__",
    "__main__",
    "_dummy_thread",
    "_thread",
    "abc",
    "aifc",
    "argparse",
    "array",
    "ast",
    "asynchat",
    "asyncio",
    "asyncore",
    "atexit",
    "audioop",
    "base64",
    "bdb",
    "binascii",
    "binhex",
    "bisect",
    "builtins",
    "bz2",
    "calendar",
    "cgi",
    "cgitb",
    "chunk",
    "cmath",
    "cmd",
    "code",
    "codecs",
    "codeop",
    "collections",
    "colorsys",
    "compileall",
    "concurrent",
    "configparser",
    "contextlib",
    "contextvars",
    "copy",
    "copyreg",
    "cProfile",
    "crypt",
    "csv",
    "ctypes",
    "curses",
    "dataclasses",
    "datetime",
    "dbm",
    "decimal",
    "difflib",
    "dis",
    "distutils",
    "doctest",
    "dummy_threading",
    "email",
    "encodings",
    "ensurepip",
    "enum",
    "errno",
    "faulthandler",
    "fcntl",
    "filecmp",
    "fileinput",
    "fnmatch",
    "formatter",
    "fractions",
    "ftplib",
    "functools",
    "gc",
    "getopt",
    "getpass",
    "gettext",
    "glob",
    "grp",
    "gzip",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "imaplib",
    "imghdr",
    "imp",
    "importlib",
    "inspect",
    "io",
    "ipaddress",
    "itertools",
    "json",
    "keyword",
    "lib2to3",
    "linecache",
    "locale",
    "logging",
    "lzma",
    "macpath",
    "mailbox",
    "mailcap",
    "marshal",
    "math",
    "mimetypes",
    "mmap",
    "modulefinder",
    "msilib",
    "msvcrt",
    "multiprocessing",
    "netrc",
    "nis",
    "nntplib",
    "numbers",
    "operator",
    "optparse",
    "os",
    "ossaudiodev",
    "parser",
    "pathlib",
    "pdb",
    "pickle",
    "pickletools",
    "pipes",
    "pkgutil",
    "platform",
    "plistlib",
    "poplib",
    "posix",
    "pprint",
    "profile",
    "pstats",
    "pty",
    "pwd",
    "py_compile",
    "pyclbr",
    "pydoc",
    "queue",
    "quopri",
    "random",
    "re",
    "readline",
    "reprlib",
    "resource",
    "rlcompleter",
    "runpy",
    "sched",
    "secrets",
    "select",
    "selectors",
    "shelve",
    "shlex",
    "shutil",
    "signal",
    "site",
    "smtpd",
    "smtplib",
    "sndhdr",
    "socket",
    "socketserver",
    "spwd",
    "sqlite3",
    "ssl",
    "stat",
    "statistics",
    "string",
    "stringprep",
    "struct",
    "subprocess",
    "sunau",
    "symbol",
    "symtable",
    "sys",
    "sysconfig",
    "syslog",
    "tabnanny",
    "tarfile",
    "telnetlib",
    "tempfile",
    "termios",
    "textwrap",
    "threading",
    "time",
    "timeit",
    "tkinter",
    "token",
    "tokenize",
    "trace",
    "traceback",
    "tracemalloc",
    "tty",
    "turtle",
    "turtledemo",
    "types",
    "typing",
    "unicodedata",
    "unittest",
    "urllib",
    "uu",
    "uuid",
    "venv",
    "warnings",
    "wave",
    "weakref",
    "webbrowser",
    "winreg",
    "winsound",
    "wsgiref",
    "xdrlib",
    "xml",
    "xmlrpc",
    "zipapp",
    "zipfile",
    "zipimport",
    "zlib",
}


class ProgramNamingAnalyzer(ProgramAnalyzer):
    def start_analysis(self, main_file_path, imported_file_paths):
        self.completion_handler(self, list(self._get_warnings(main_file_path)))

    def _get_warnings(self, main_file_path):
        from thonny import rst_utils

        # TODO: current dir may be different
        main_file_dir = os.path.dirname(main_file_path)
        if not os.path.isdir(main_file_dir):
            return

        library_modules = known_stdlib_modules | self._get_3rd_party_modules()

        for item in os.listdir(main_file_dir):
            full_path = os.path.join(main_file_dir, item)
            if item.endswith(".py") and item[:-3] in library_modules:

                if is_same_path(full_path, main_file_path):
                    prelude = "Your program file is named '%s'." % item
                    rename_hint = " (*File → Rename…* )"
                else:
                    prelude = (
                        "Your working directory `%s <%s>`__ contains a file named '%s'.\n\n"
                        % (rst_utils.escape(main_file_dir), rst_utils.escape(main_file_dir), item)
                    )
                    rename_hint = ""

                yield {
                    "filename": full_path,
                    "lineno": 0,
                    "symbol": "file-shadows-library-module",
                    "msg": "Possibly bad file name",
                    "explanation_rst": prelude
                    + "\n\n"
                    + "When you try to import library module ``%s``, your file will be imported instead.\n\n"
                    % item[:-3]
                    + "Rename your '%s'%s to make the library module visible again."
                    % (item, rename_hint),
                    "group": "warnings",
                    "relevance": 5,
                }

    def _get_3rd_party_modules(self):
        proxy = get_runner().get_backend_proxy()
        from thonny.plugins.cpython import CPythonProxy

        if not isinstance(proxy, CPythonProxy):
            return []

        try:
            sys_path = proxy.get_sys_path()
        except Exception:
            logging.exception("Can't get sys path from proxy")
            return []

        module_names = set()
        for item in sys_path:
            if os.path.isdir(item) and ("site-packages" in item or "dist-packages" in item):
                module_names.update(self._get_module_names(item))
                for name in os.listdir(item):
                    if "-" not in name:
                        module_names.add(name.replace(".py", ""))

        return module_names

    def _get_module_names(self, dir_path):
        result = set()
        for name in os.listdir(dir_path):
            if "-" not in name:
                result.add(name.replace(".py", ""))
        return result


def load_plugin():
    add_program_analyzer(ProgramNamingAnalyzer)
