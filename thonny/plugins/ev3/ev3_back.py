import os.path
import sys
from logging import getLogger
from typing import List, Optional

import thonny
from thonny.plugins.micropython.os_mp_backend import SshUnixMicroPythonBackend

logger = getLogger("thonny.plugins.ev3.ev3_back")


class EV3MicroPythonBackend(SshUnixMicroPythonBackend):
    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return [
            os.path.join(os.path.dirname(__file__), "api_stubs"),
        ] + super()._get_sys_path_for_analysis()


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    thonny.configure_backend_logging()

    import ast

    args = ast.literal_eval(sys.argv[1])

    EV3MicroPythonBackend(args)
