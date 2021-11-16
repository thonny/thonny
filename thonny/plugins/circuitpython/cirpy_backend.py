from logging import getLogger
import time

from thonny.plugins.micropython.backend import INTERRUPT_CMD, SOFT_REBOOT_CMD
from thonny.plugins.micropython.bare_metal_backend import (
    BareMetalMicroPythonBackend,
    launch_bare_metal_backend,
)

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.cirpy_backend")


class CircuitPythonBackend(BareMetalMicroPythonBackend):
    def _create_fresh_repl(self):
        """
        CP runs code.py after soft-reboot even in raw repl.
        At the same time, it creates fresh VM after entering REPL, so it's enough to order a
        soft reboot (which won't run boot.py) and then interrupt the main script.
        """
        logger.info("Creating fresh REPL for CP")
        self._write(SOFT_REBOOT_CMD)

        """
        logger.debug("Extra interrupts for CP")
        # The first extra interrupt is required getting past the banner
        # "Press any key to enter REPL"
        # The others are just in case...
        # (maybe the main script caught KeyboardInterrupt or something ...)

        self._write(INTERRUPT_CMD)
        time.sleep(0.05)
        self._write(INTERRUPT_CMD)
        time.sleep(0.3)
        self._write(INTERRUPT_CMD)
        time.sleep(0.05)
        self._write(INTERRUPT_CMD)
        """

        # TODO: interrupt more if the prompt doesn't appear in time
        self._log_output_until_active_prompt(
            interrupt_times=[0.01, 0.02, 0.03, 0.11, 0.12, 0.13, 1.1, 1.2, 1.3]
        )


if __name__ == "__main__":
    launch_bare_metal_backend(CircuitPythonBackend)
