from thonny.plugins.micropython.backend import MicroPythonBackend
import textwrap
from textwrap import dedent
from thonny.common import UserError

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


class MicroPythonOsBackend(MicroPythonBackend):
    def _prepare_helpers(self):
        script = textwrap.dedent(
            """
            import sys as _thonny_sys
            import ffi as _thonny_ffi
            
            _thonny_sys.modules["_thonny_libc"] = _thonny_ffi.open(
                "libc.so.6" if _thonny_sys.platform == "linux" else "libc.dylib"
            )
            
            del _thonny_sys
            del _thonny_ffi
        """
        )
        self._execute_without_errors(script)

    def _process_until_initial_prompt(self, clean):
        raise NotImplementedError()

    def _fetch_welcome_text(self):
        impl_ver = self._evaluate(
            "_thonny_sys.implementation.version", "import sys as _thonny_sys", "del _thonny_sys"
        )

        return "MicroPython " + ".".join(impl_ver) + "\n"

    def _fetch_builtin_modules(self):
        return FALLBACK_BUILTIN_MODULES

    def _fetch_cwd(self):
        self._evaluate(
            "_thonny_getcwd(_thonny_buf, 512)",
            dedent(
                """
                import sys as _thonny_sys
                _thonny_buf = bytearray(512)
                _thonny_getcwd = _thonny_sys.modules["_thonny_libc"].func("s", "getcwd", "si")
            """
            ),
            dedent(
                """
                del _thonny_sys
                del _thonny_buf
                del _thonny_getcwd
            """
            ),
        )

    def _soft_reboot(self, side_command):
        raise NotImplementedError()

    def _execute(self, script, timeout, capture_stdout):
        """Ensures prompt and submits the script.
        Returns (out, value_repr, err) if there are no problems, ie. all parts of the 
        output are present and it reaches active prompt.
        Otherwise raises ProtocolError.
        
        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        raise NotImplementedError()

    def _forward_output_until_active_prompt(self, stream_name="stdout"):
        """Used for finding initial prompt or forwarding problematic output 
        in case of protocol errors"""
        raise NotImplementedError()

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        raise NotImplementedError()

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            path = cmd.args[0]
            self._execute_without_errors(
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
