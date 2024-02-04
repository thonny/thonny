import os.path
from typing import List, Optional

from thonny.plugins.micropython.bare_metal_backend import BareMetalMicroPythonBackend


class SimplifiedMicroPythonBackend(BareMetalMicroPythonBackend):
    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return [
            os.path.join(os.path.dirname(__file__), "api_stubs"),
        ]
