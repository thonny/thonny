import datetime
import io
import logging
import os
import re
import shlex
import sys
import textwrap
import time
from abc import ABC
from typing import Callable, Optional, Union

import thonny
from thonny.backend import SshMixin
from thonny.common import BackendEvent, serialize_message
from thonny.plugins.micropython.backend import (
    ENCODING,
    EOT,
    MicroPythonBackend,
    ends_overlap,
    ManagementError,
    PASTE_MODE_CMD,
    PASTE_MODE_LINE_PREFIX,
)
from thonny.plugins.micropython.bare_metal_backend import LF, NORMAL_PROMPT, PASTE_SUBMIT_MODE
from thonny.common import ConnectionFailedException

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
        except ConnectionFailedException as e:
            text = "\n" + str(e) + "\n"
            msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
            sys.stdout.write(serialize_message(msg) + "\n")
            sys.stdout.flush()
            return

        MicroPythonBackend.__init__(self, None, args)

    def _resolve_executable(self, executable):
        result = self._which(executable)
        if result:
            return result
        else:
            msg = "Executable '%s' not found. Please check your configuration!" % executable
            if not executable.startswith("/"):
                msg += " You may need to provide its absolute path."
            raise ConnectionFailedException(msg)

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

    def _get_custom_helpers(self):
        return textwrap.dedent(
            """
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
        # This will be called only when the interpreter gets run without script.
        # (%Run script.py does not create a new instance of this class)
        output = []

        def collect_output(data, stream_name):
            output.append(data)

        self._report_time("befini")
        self._forward_output_until_active_prompt(collect_output, "stdout")
        self._original_welcome_text = "".join(output).replace("\r\n", "\n")
        self._welcome_text = self._tweak_welcome_text(self._original_welcome_text)
        self._report_time("afini")

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
        self._connection.write(PASTE_MODE_CMD)
        self._connection.read_until(PASTE_MODE_LINE_PREFIX)
        self._connection.write(script + end_marker)
        self._connection.read_until(end_marker.encode("ascii"))
        self._connection.write(EOT)
        self._connection.read_until(b"\n")
        self._forward_output_until_active_prompt(output_consumer)

    def _forward_output_until_active_prompt(
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

    def _write(self, data):
        self._connection.write(data)

    def _cmd_Run(self, cmd):
        self._connection.close()
        self._report_time("befconn")
        args = cmd.args
        if cmd.source and args[0] == "-c":
            if len(args) > 1:
                self._send_error_message(
                    "Warning: MicroPython doesn't allow program arguments (%s) together with '-c'"
                    % " ".join(map(shlex.quote, args[1:]))
                )
            args = ["-c", cmd.source]

        self._connection = self._create_connection(args)
        self._report_time("afconn")
        self._forward_output_until_active_prompt(self._send_output, "stdout")
        self._report_time("afforv")
        self.send_message(
            BackendEvent(event_type="HideTrailingOutput", text=self._original_welcome_text)
        )
        self._report_time("beffhelp")
        self._prepare_after_soft_reboot()
        self._report_time("affhelp")

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
        except Exception:
            raise ManagementError(script, out, err)

    def _is_connected(self):
        return not self._connection._error

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

    def _submit_input(self, cdata: str) -> None:
        # TODO: what if there is a previous unused data waiting
        assert self._connection.outgoing_is_empty()

        assert cdata.endswith("\n")
        if not cdata.endswith("\r\n"):
            # submission is done with CRLF
            cdata = cdata[:-1] + "\r\n"

        bdata = cdata.encode(ENCODING)
        to_be_written = bdata
        echo = b""
        with self._interrupt_lock:
            self._write(to_be_written)
            # Try to consume the echo
            echo += self._connection.soft_read(len(to_be_written), timeout=1)

        if echo.replace(b"\r", b" ").replace(b"\n", b" ") != bdata.replace(b"\r", b" ").replace(
            b"\n", b" "
        ):
            # because of autoreload? timing problems? interruption?
            # Leave it.
            logging.warning("Unexpected echo. Expected %r, got %r" % (bdata, echo))
            self._connection.unread(echo)


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


class SshUnixMicroPythonBackend(UnixMicroPythonBackend, SshMixin):
    def __init__(self, args):
        SshMixin.__init__(
            self, args["host"], args["user"], args["password"], args["interpreter"], args.get("cwd")
        )
        UnixMicroPythonBackend.__init__(self, args)

    def _which(self, executable):
        cmd_str = " ".join(map(shlex.quote, ["which", executable]))
        _, stdout, _ = self._client.exec_command(cmd_str, bufsize=0, timeout=3, get_pty=False)
        return stdout.readline().strip() or None

    def _create_connection(self, run_args=[]):
        # NB! It's connection to the micropython process, not to the host
        from thonny.plugins.micropython.ssh_connection import SshProcessConnection

        return SshProcessConnection(self._client, self._cwd, self._interpreter, ["-i"] + run_args)

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


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    thonny.configure_backend_logging()

    import ast

    args = ast.literal_eval(sys.argv[1])

    if "host" in args:
        backend = SshUnixMicroPythonBackend(args)
    else:
        backend = LocalUnixMicroPythonBackend(args)
