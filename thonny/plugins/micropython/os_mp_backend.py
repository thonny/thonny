from logging import getLogger

import os
import sys
from abc import ABC
from minny.common import ManagementError
from minny.os_target import LocalOsTargetManager
from typing import Any, Dict

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.insert(0, thonny_container)

import thonny
from thonny.common import PROCESS_ACK
from thonny.plugins.micropython.mp_back import MicroPythonBackend

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.os_mp_backend")


class UnixMicroPythonBackend(MicroPythonBackend, ABC):
    def _cmd_execute_system_command(self, cmd) -> Dict[str, Any]:
        assert cmd.cmd_line.startswith("!")
        cmd_line = cmd.cmd_line[1:]
        returncode = self._evaluate("__minny_helper.os.system(%r)" % cmd_line)
        return {"returncode": returncode}

    def _cmd_get_fs_info(self, cmd):
        script = """__minny_helper.os.system("stat -f -c '%b %f %a %S' {path}") or None""".format(
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
    def __init__(self, args: Dict[str, Any]):
        tmgr = LocalOsTargetManager(args["interpreter"])
        super().__init__(tmgr, args)

    def _cmd_cd(self, cmd):
        result = super()._cmd_cd(cmd)

        # need to change also for this process, not only for the micropython subprocess
        cwd = self._tmgr.get_cwd()
        assert cwd is not None
        os.chdir(cwd)
        return result


"""
class SshUnixMicroPythonBackend(UnixMicroPythonBackend, SshMixin):
    def __init__(self, args: Dict[str, Any]):
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
        super().__init__(args)

    def _create_manager(self, interpreter: str, launch_args: List[str]) -> OsTargetManager:
        return LocalOsTargetManager(interpreter, launch_args)
"""


if __name__ == "__main__":
    thonny.configure_backend_logging()
    print(PROCESS_ACK)

    import ast

    args = ast.literal_eval(sys.argv[1])

    if "host" in args:
        # backend = SshUnixMicroPythonBackend(args)
        raise NotImplementedError("ssh backend out of order")
    else:
        backend = LocalUnixMicroPythonBackend(args)
