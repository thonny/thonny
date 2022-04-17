import os.path
import sys
from typing import List, Optional

import thonny
from thonny.plugins.micropython.os_mp_backend import SshUnixMicroPythonBackend


class EV3MicroPythonBackend(SshUnixMicroPythonBackend):
    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return [
            os.path.join(os.path.dirname(__file__), "api_stubs"),
        ]


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    thonny.configure_backend_logging()

    import ast

    args = ast.literal_eval(sys.argv[1])

    EV3MicroPythonBackend(args)
