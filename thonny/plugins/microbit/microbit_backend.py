from logging import getLogger

from thonny.plugins.micropython.bare_metal_backend import (
    BareMetalMicroPythonBackend,
    launch_bare_metal_backend,
)

logger = getLogger(__name__)


class MicrobitMicroPythonBackend(BareMetalMicroPythonBackend):
    pass


if __name__ == "__main__":
    launch_bare_metal_backend(MicrobitMicroPythonBackend)
