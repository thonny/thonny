from logging import getLogger

from thonny.plugins.micropython.bare_metal_backend import (
    BareMetalMicroPythonBackend,
    launch_bare_metal_backend,
)

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.microbit_backend")


class MicrobitMicroPythonBackend(BareMetalMicroPythonBackend):
    pass


if __name__ == "__main__":
    launch_bare_metal_backend(MicrobitMicroPythonBackend)
