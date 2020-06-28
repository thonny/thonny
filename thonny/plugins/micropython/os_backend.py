import os
import sys
import logging
from thonny.plugins.micropython.backend import MicroPythonBackend, EOT
import textwrap
from textwrap import dedent
from thonny.common import UserError, BackendEvent, serialize_message
from thonny.plugins.micropython.subprocess_connection import SubprocessConnection
from thonny.plugins.micropython.connection import ConnectionFailedException
from thonny.plugins.micropython.bare_metal_backend import NORMAL_PROMPT

FALLBACK_BUILTIN_MODULES = [
    "cmath",
    "gc",
    "math",
    "sys",
    "array",
    # "binascii", # don't include it, as it may give false signal for reader/writer
    "collections",
    "errno",
    "hashlib",
    "heapq",
    "io",
    "json",
    "os",
    "re",
    "select",
    "socket",
    "ssl",
    "struct",
    "time",
    "zlib",
    "_thread",
    "btree",
    "micropython",
    "cryptolib",
    "ctypes",
]

PASTE_MODE_CMD = b"\x05"
PASTE_MODE_LINE_PREFIX = b"=== "


class MicroPythonOsBackend(MicroPythonBackend):
    def __init__(self, connection, clean, api_stubs_path):
        self._connection = connection
        super().__init__(clean, api_stubs_path)

    def _get_custom_helpers(self):
        return textwrap.dedent(
            """
            if not hasattr(os, "getcwd") or not hasattr(os, "getcwd") or not hasattr(os, "rmdir"):
                # https://github.com/pfalcon/pycopy-lib/blob/master/os/os/__init__.py
                
                import ffi
                
                libc = ffi.open(
                    "libc.so.6" if sys.platform == "linux" else "libc.dylib"
                )
                
                @classmethod
                def check_error(cls, ret):
                    if ret == -1:
                        raise OSError(cls.os.errno())
                
                _getcwd = libc.func("s", "getcwd", "si")
                @classmethod
                def getcwd(cls):
                    buf = bytearray(512)
                    return cls._getcwd(buf, 512)

                _chdir = libc.func("i", "chdir", "s")
                @classmethod
                def chdir(cls, dir):
                    r = cls._chdir(dir)
                    cls.check_error(r)
                
                _rmdir = libc.func("i", "rmdir", "s")
                @classmethod
                def rmdir(cls, name):
                    e = cls._rmdir(name)
                    cls.check_error(e)                                    
                """
        )

    def _process_until_initial_prompt(self, clean):
        data = self._connection.read_until(NORMAL_PROMPT)
        self._send_output(data, "stdout")

    def _fetch_welcome_text(self):
        impl_ver = self._evaluate("__thonny_helper.sys.implementation.version")

        return "MicroPython " + ".".join(map(str, impl_ver)) + "\n"

    def _fetch_builtin_modules(self):
        return FALLBACK_BUILTIN_MODULES

    def _soft_reboot(self, side_command):
        raise NotImplementedError()

    def _execute_with_consumer(self, script, output_consumer):
        """Ensures prompt and submits the script.
        Returns (out, value_repr, err) if there are no problems, ie. all parts of the 
        output are present and it reaches active prompt.
        Otherwise raises ProtocolError.
        
        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        self._connection.write(PASTE_MODE_CMD)
        self._connection.read_until(PASTE_MODE_LINE_PREFIX)
        self._connection.write(script + "#uuu")
        self._connection.read_until(b"#uuu")
        self._connection.write(EOT)
        self._connection.read_until(b"\n")

        out = self._connection.read_until(NORMAL_PROMPT)[: -len(NORMAL_PROMPT)]
        output_consumer(out, "stdout")

    def _forward_output_until_active_prompt(self, stream_name="stdout"):
        """Used for finding initial prompt or forwarding problematic output 
        in case of protocol errors"""
        raise NotImplementedError()

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        pass
        # TODO:

    def _write(self, data):
        raise NotImplementedError()

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            path = cmd.args[0]
            self._execute_without_output(
                dedent(
                    """
                import sys as _thonny_sys
                try:
                    if _thonny_sys.modules["_thonny_libc"].func("i", "chdir", "s")(%r) != 0:
                        raise OSError("cd failed")
                finally:
                    del _thonny_sys
            """
                )
                % path
            )
            self._cwd = self._fetch_cwd()
            return {}
        else:
            raise UserError("%cd takes one parameter")

    def _cmd_execute_system_command(self, cmd):
        raise NotImplementedError()

    def _cmd_get_fs_info(self, cmd):
        raise NotImplementedError()

    def _cmd_write_file(self, cmd):
        raise NotImplementedError()

    def _cmd_delete(self, cmd):
        raise NotImplementedError()

    def _cmd_read_file(self, cmd):
        raise NotImplementedError()

    def _cmd_mkdir(self, cmd):
        raise NotImplementedError()

    def _upload_file(self, source, target, notifier):
        raise NotImplementedError()

    def _download_file(self, source, target, notifier=None):
        raise NotImplementedError()

    def _is_connected(self):
        return not self._connection._error


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    logger = logging.getLogger("thonny.micropython.backend")
    logger.propagate = False
    logFormatter = logging.Formatter("%(levelname)s: %(message)s")
    file_handler = logging.FileHandler(
        os.path.join(THONNY_USER_DIR, "micropython-backend.log"), encoding="UTF-8", mode="w"
    )
    file_handler.setFormatter(logFormatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=str)
    parser.add_argument("--api_stubs_path", type=str)
    args = parser.parse_args()

    try:
        connection = SubprocessConnection(args.executable, ["-i"], None)
        vm = MicroPythonOsBackend(connection, clean=None, api_stubs_path=args.api_stubs_path)
    except ConnectionFailedException as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
