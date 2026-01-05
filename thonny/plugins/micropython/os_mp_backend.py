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
from thonny.common import ALL_EXPLAINED_STATUS_CODE, PROCESS_ACK, BackendEvent, serialize_message
from thonny.plugins.micropython.bare_metal_backend import LF, NORMAL_PROMPT
from thonny.plugins.micropython.connection import MicroPythonConnection
from thonny.plugins.micropython.mp_back import (
    ENCODING,
    EOT,
    PASTE_MODE_CMD,
    PASTE_MODE_LINE_PREFIX,
    MicroPythonBackend,
    ends_overlap,
)
from thonny.plugins.micropython.mp_common import PASTE_SUBMIT_MODE

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.os_mp_backend")




class UnixMicroPythonBackend(MicroPythonBackend, ABC):
    def __init__(self, args):
        # TODO:
        self._tmgr = self._create_target_manger()

        MicroPythonBackend.__init__(self, None, args)


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
            source = cmd.source
        else:
            logger.info("Omitting source_for_langage_server, as it is not readily available")
            source = None

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

        if source is not None:
            return {"source_for_language_server": source}
        else:
            return {}

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


class LocalUnixMicroPythonBackend(UnixMicroPythonBackend):

    def _cmd_cd(self, cmd):
        result = super()._cmd_cd(cmd)
        os.chdir(self._cwd)
        return result

    def _create_target_manager(self):
        raise NotImplementedError()


class SshUnixMicroPythonBackend(UnixMicroPythonBackend, SshMixin):
    def __init__(self, args):
        password = sys.stdin.readline().strip("\r\n")
        SshMixin.__init__(
            self,
            args["host"],
            args["port"],
            args["user"],
            password,
            args["interpreter"],
            args.get("cwd"),
        )
        self._interpreter_launcher = args.get("interpreter_launcher", [])
        UnixMicroPythonBackend.__init__(self, args)



if __name__ == "__main__":
    thonny.configure_backend_logging()
    print(PROCESS_ACK)

    import ast

    args = ast.literal_eval(sys.argv[1])

    if "host" in args:
        backend = SshUnixMicroPythonBackend(args)
    else:
        backend = LocalUnixMicroPythonBackend(args)
