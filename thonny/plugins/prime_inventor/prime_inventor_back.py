import os.path
import sys
from logging import getLogger
from typing import List, Optional

import thonny
from thonny.plugins.micropython.bare_metal_backend import (
    BareMetalMicroPythonBackend,
    launch_bare_metal_backend,
)

logger = getLogger("thonny.plugins.prime_inventor.prime_inventor_back")


class PrimeInventorMicroPythonBackend(BareMetalMicroPythonBackend):
    pass


if __name__ == "__main__":
    launch_bare_metal_backend(PrimeInventorMicroPythonBackend)
