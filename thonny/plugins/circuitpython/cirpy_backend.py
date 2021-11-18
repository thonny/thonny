import os.path
from logging import getLogger
from textwrap import dedent

import time

from thonny.plugins.micropython.backend import SOFT_REBOOT_CMD
from thonny.plugins.micropython.bare_metal_backend import (
    BareMetalMicroPythonBackend,
    launch_bare_metal_backend,
)

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.cirpy_backend")


class CircuitPythonBackend(BareMetalMicroPythonBackend):
    def _clear_repl(self):
        """
        CP runs code.py after soft-reboot even in raw repl.
        At the same time, it re-initializes VM and hardware just by switching
        between raw and friendly REPL (tested in CP 6.3 and 7.1)
        """
        logger.info("Creating fresh REPL for CP")
        self._ensure_normal_mode()
        self._ensure_raw_mode()



if __name__ == "__main__":
    launch_bare_metal_backend(CircuitPythonBackend)
