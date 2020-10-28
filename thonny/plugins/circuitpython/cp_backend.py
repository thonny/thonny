import logging
import time

from thonny.plugins.micropython.backend import INTERRUPT_CMD
from thonny.plugins.micropython.bare_metal_backend import BareMetalMicroPythonBackend

logger = logging.getLogger(__name__)


class CircuitPythonBackend(BareMetalMicroPythonBackend):
    def _extra_interrupts_after_soft_reboot(self):
        logger.debug("Extra interrupts for CP")
        # CP runs code.py after soft-reboot even in raw repl, so I'll send some Ctrl-C to intervene
        # # (they don't do anything when already in raw repl)
        self._write(INTERRUPT_CMD)
        self._write(INTERRUPT_CMD)
        time.sleep(0.5)
        self._write(INTERRUPT_CMD)
        time.sleep(0.1)
        self._write(INTERRUPT_CMD)
