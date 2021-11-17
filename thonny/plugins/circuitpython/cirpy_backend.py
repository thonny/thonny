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
        At the same time, it creates fresh VM after entering REPL, so it's enough to order a
        soft reboot (which won't run boot.py) and then interrupt the main script.
        """
        logger.info("Creating fresh REPL for CP")

        # Try avoiding executing code.py
        # NB! This must be done without __thonny_helper!
        helper_file = "/.next_code_file_for_clear_repl"
        # stat-ing the file to see if it exists
        self._execute_without_output(
            dedent(
                f"""
            import os
            try:
                os.stat({helper_file!r})  
                import supervisor
                supervisor.set_next_code_file({helper_file!r})
            except:
                pass
            """
            )
        )

        self._write(SOFT_REBOOT_CMD)
        self._interrupt()

        # first couple of the extra interrupts should usually suffice
        self._log_output_until_active_prompt(
            interrupt_times=[0.01, 0.02, 0.03, 0.11, 0.12, 0.13, 1.1, 1.2, 1.3]
        )


if __name__ == "__main__":
    launch_bare_metal_backend(CircuitPythonBackend)
