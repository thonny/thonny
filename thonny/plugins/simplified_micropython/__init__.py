from minny.target import PASTE_SUBMIT_MODE

from thonny.languages import tr
from thonny.plugins.micropython import _migrate_device_backends, add_micropython_backend
from thonny.plugins.micropython.mp_front import VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND
from thonny.plugins.simplified_micropython.simplified_mp_front import (
    SimplifiedMicroPythonConfigPage,
    SimplifiedMicroPythonProxy,
)

_BACKEND_NAME = "SimplifiedMicroPython"


def load_plugin():
    add_micropython_backend(
        _BACKEND_NAME,
        SimplifiedMicroPythonProxy,
        tr("Device MicroPython (simplified)"),
        SimplifiedMicroPythonConfigPage,
        sort_key="32",
        sync_time=False,
        submit_mode=PASTE_SUBMIT_MODE,
        write_block_size=128,
    )

    # Keep these ports out of automatic discovery for generic MicroPython.
    VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        SimplifiedMicroPythonProxy.get_known_usb_vids_pids()
    )
    _migrate_device_backends(_BACKEND_NAME, ("microbit", "calliope"))
