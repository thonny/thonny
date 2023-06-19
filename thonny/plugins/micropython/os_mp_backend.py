import datetime
import io
import os
import re
import shlex
import sys
import textwrap
import time
from abc import ABC
from logging import getLogger
from typing import Callable, Optional, Union

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.insert(0, thonny_container)

import thonny
from thonny import report_time
from thonny.backend import SshMixin
from thonny.common import PROCESS_ACK, BackendEvent, serialize_message
from thonny.plugins.micropython.bare_metal_backend import LF, NORMAL_PROMPT
from thonny.plugins.micropython.connection import MicroPythonConnection
from thonny.plugins.micropython.mp_back import (
    ENCODING,
    EOT,
    PASTE_MODE_CMD,
    PASTE_MODE_LINE_PREFIX,
    ManagementError,
    MicroPythonBackend,
    ends_overlap,
)
from thonny.plugins.micropython.mp_common import PASTE_SUBMIT_MODE

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.os_mp_backend")


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


class UnixMicroPythonBackend(MicroPythonBackend, ABC):
    def __init__(self, args):
        try:
            self._interpreter = self._resolve_executable(args["interpreter"])
            self._connection = self._create_connection()
        except ConnectionRefusedError as e:
            text = "\n" + str(e) + "\n"
            msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
            sys.stdout.write(serialize_message(msg) + "\n")
            sys.stdout.flush()
            sys.exit(1)

        MicroPythonBackend.__init__(self, None, args)

    def get_connection(self) -> MicroPythonConnection:
        return self._connection

    def _resolve_executable(self, executable):
        result = self._which(executable)
        if result:
            return result
        else:
            msg = "Executable '%s' not found. Please check your configuration!" % executable
            if not executable.startswith("/"):
                msg += " You may need to provide its absolute path."
            raise ConnectionRefusedError(msg)

    def _which(self, executable):
        raise NotImplementedError()

    def _create_connection(self, run_args=[]):
        raise NotImplementedError()

    def _tweak_welcome_text(self, original: str) -> str:
        return (
            original.replace("Use Ctrl-D to exit, Ctrl-E for paste mode\n", "").strip()
            + " ("
            + self._interpreter
            + ")\n"
        )

    def _get_helper_code(self):
        extra = textwrap.dedent(
            """
            # https://github.com/pfalcon/pycopy-lib/blob/master/os/os/__init__.py
            
            import ffi
            
            libc = ffi.open(
                "libc.so.6" if sys.platform == "linux" else "libc.dylib"
            )
            
            @builtins.classmethod
            def check_error(cls, ret):
                if ret == -1:
                    raise cls.builtins.OSError(cls.os.errno())
            
            _getcwd = libc.func("s", "getcwd", "si")
            @builtins.classmethod
            def getcwd(cls):
                buf = cls.builtins.bytearray(512)
                return cls._getcwd(buf, 512)

            _chdir = libc.func("i", "chdir", "s")
            @builtins.classmethod
            def chdir(cls, dir):
                r = cls._chdir(dir)
                cls.check_error(r)
            
            _rmdir = libc.func("i", "rmdir", "s")
            @builtins.classmethod
            def rmdir(cls, name):
                e = cls._rmdir(name)
                cls.check_error(e)                                    
            """
        )

        return super()._get_helper_code() + textwrap.indent(extra, "    ")

    def _process_until_initial_prompt(self, interrupt, clean):
        # This will be called only when the interpreter gets run without script.
        # (%Run script.py does not create a new instance of this class)
        output = []

        def collect_output(data, stream_name):
            output.append(data)

        report_time("befini")
        self._process_output_until_active_prompt(collect_output, "stdout")
        self._original_welcome_text = "".join(output).replace("\r\n", "\n")
        self._welcome_text = self._tweak_welcome_text(self._original_welcome_text)
        report_time("afini")

    def _fetch_builtin_modules(self):
        return FALLBACK_BUILTIN_MODULES

    def _execute_with_consumer(
        self, script: str, output_consumer: Callable[[str, str], None]
    ) -> None:
        """Ensures prompt and submits the script.
        Returns (out, value_repr, err) if there are no problems, ie. all parts of the
        output are present and it reaches active prompt.
        Otherwise raises ManagementError.

        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        end_marker = "#uIuIu"
        self._write(PASTE_MODE_CMD)
        self._connection.read_until(PASTE_MODE_LINE_PREFIX)
        self._write((script + end_marker).encode(ENCODING))
        self._connection.read_until(end_marker.encode("ascii"))
        self._write(EOT)
        self._connection.read_until(b"\n")
        self._process_output_until_active_prompt(output_consumer)

    def _process_output_until_active_prompt(
        self, output_consumer: Callable[[str, str], None], stream_name="stdout"
    ):
        INCREMENTAL_OUTPUT_BLOCK_CLOSERS = re.compile(
            b"|".join(map(re.escape, [LF, NORMAL_PROMPT]))
        )

        pending = b""
        while True:
            # There may be an input submission waiting
            # and we can't progress without resolving it first
            self._check_for_side_commands()

            # Prefer whole lines, but allow also incremental output to single line
            new_data = self._connection.soft_read_until(
                INCREMENTAL_OUTPUT_BLOCK_CLOSERS, timeout=0.05
            )
            if not new_data:
                continue

            pending += new_data

            if pending.endswith(LF):
                output_consumer(self._decode(pending), stream_name)
                pending = b""

            elif pending.endswith(NORMAL_PROMPT):
                out = pending[: -len(NORMAL_PROMPT)]
                output_consumer(self._decode(out), stream_name)
                return NORMAL_PROMPT

            elif ends_overlap(pending, NORMAL_PROMPT):
                # Maybe we have a prefix of the prompt and the rest is still coming?
                follow_up = self._connection.soft_read(1, timeout=0.1)
                if not follow_up:
                    # most likely not a Python prompt, let's forget about it
                    output_consumer(self._decode(pending), stream_name)
                    pending = b""
                else:
                    # Let's withhold this for now
                    pending += follow_up

            else:
                # No prompt in sight.
                # Output and keep working.
                output_consumer(self._decode(pending), stream_name)
                pending = b""

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        data = self._connection.read_all()
        if data.endswith(NORMAL_PROMPT):
            out = data[: -len(NORMAL_PROMPT)]
        else:
            out = data
        self._send_output(self._decode(out), "stdout")

    def _cmd_Run(self, cmd):
        self._connection.close()
        report_time("befconn")
        args = cmd.args
        if cmd.source and args[0] == "-c":
            if len(args) > 1:
                self._send_error_message(
                    "Warning: MicroPython doesn't allow program arguments (%s) together with '-c'"
                    % " ".join(map(shlex.quote, args[1:]))
                )
            args = ["-c", cmd.source]

        self._connection = self._create_connection(args)
        report_time("afconn")
        self._process_output_until_active_prompt(self._send_output, "stdout")
        report_time("afforv")
        self.send_message(
            BackendEvent(event_type="HideTrailingOutput", text=self._original_welcome_text)
        )
        report_time("beffhelp")
        self._prepare_after_soft_reboot()
        report_time("affhelp")

    def _cmd_execute_system_command(self, cmd):
        assert cmd.cmd_line.startswith("!")
        cmd_line = cmd.cmd_line[1:]
        # "or None" in order to avoid MP repl to print its value
        self._execute("__thonny_helper.os.system(%r) or None" % cmd_line)
        # TODO: report returncode

    def _cmd_get_fs_info(self, cmd):
        script = """__thonny_helper.os.system("stat -f -c '%b %f %a %S' {path}") or None""".format(
            path=cmd.path
        )
        out, err = self._execute(script, capture_output=True)

        try:
            total, free, available, block_size = map(int, out.strip().split())
            return {
                "total": total * block_size,
                "free": available * block_size,
                "used": (total - free) * block_size,
            }
        except Exception as e:
            raise ManagementError("Could not parse disk information", script, out, err) from e

    def _get_epoch_offset(self) -> int:
        try:
            return super()._get_epoch_offset()
        except NotImplementedError:
            return 0

    def _resolve_unknown_epoch(self) -> int:
        return 1970

    def _sync_time(self):
        self._show_error("WARNING: Automatic time synchronization by Thonny is not supported.")

    def _get_utc_timetuple_from_device(self) -> Union[tuple, str]:
        out, err = self._execute("__thonny_helper.os.system('date -u +%s')", capture_output=True)
        if err:
            return err

        if not out:
            return "Failed querying device's UTC time"

        try:
            secs = int(out.splitlines()[0].strip())
            return tuple(time.gmtime(secs))
        except Exception as e:
            return str(e)

    def _extract_block_without_splitting_chars(self, source_bytes: bytes) -> bytes:
        return source_bytes


class LocalUnixMicroPythonBackend(UnixMicroPythonBackend):
    def _create_connection(self, run_args=[]):
        from thonny.plugins.micropython.subprocess_connection import SubprocessConnection

        return SubprocessConnection(self._interpreter, ["-i"] + run_args)

    def _which(self, executable):
        import shutil

        return shutil.which(executable)

    def _cmd_cd(self, cmd):
        result = super()._cmd_cd(cmd)
        os.chdir(self._cwd)
        return result

    def _get_sep(self) -> str:
        return os.path.sep

    def _decode(self, data: bytes) -> str:
        return data.decode(errors="replace")

    def _create_pipkin_adapter(self):
        raise NotImplementedError()


class SshUnixMicroPythonBackend(UnixMicroPythonBackend, SshMixin):
    def __init__(self, args):
        password = sys.stdin.readline().strip("\r\n")
        SshMixin.__init__(
            self, args["host"], args["user"], password, args["interpreter"], args.get("cwd")
        )
        self._interpreter_launcher = args.get("interpreter_launcher", [])
        UnixMicroPythonBackend.__init__(self, args)

    def _which(self, executable):
        cmd_str = " ".join(map(shlex.quote, ["which", executable]))
        _, stdout, _ = self._client.exec_command(cmd_str, bufsize=0, timeout=3, get_pty=False)
        return stdout.readline().strip() or None

    def _create_connection(self, run_args=[]):
        # NB! It's connection to the micropython process, not to the host
        from thonny.plugins.micropython.ssh_connection import SshProcessConnection

        return SshProcessConnection(
            self._client,
            self._cwd,
            self._interpreter_launcher + [self._interpreter] + ["-i"] + run_args,
        )

    def _tweak_welcome_text(self, original):
        return (
            super()._tweak_welcome_text(original).strip()
            + "\n"
            + self._user
            + "@"
            + self._host
            + "\n"
        )

    def _get_sep(self) -> str:
        return "/"

    def _decode(self, data: bytes) -> str:
        return data.decode(ENCODING, errors="replace")

    def _create_pipkin_adapter(self):
        raise NotImplementedError()


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    thonny.configure_backend_logging()
    print(PROCESS_ACK)

    import ast

    args = ast.literal_eval(sys.argv[1])

    if "host" in args:
        backend = SshUnixMicroPythonBackend(args)
    else:
        backend = LocalUnixMicroPythonBackend(args)
