from logging import getLogger
from typing import Optional

from thonny import get_workbench, ui_utils
from thonny.plugins.micropython import add_micropython_backend
from thonny.plugins.micropython.mp_common import RAW_PASTE_SUBMIT_MODE
from thonny.plugins.micropython.mp_front import get_uart_adapter_vids_pids
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog
from thonny.plugins.rp2040 import RP2040BackendConfigPage, RP2040BackendProxy
from thonny.ui_utils import show_dialog

logger = getLogger(__name__)

class Pololu3pi2040RobotBackendProxy(RP2040BackendProxy):
    @classmethod
    def should_consider_unknown_devices(cls):
        return False

    @classmethod
    def get_known_usb_vids_pids(cls):
        return {(0x1FFB, 0x2043)}

    @classmethod
    def get_node_label(self):
        return "Pololu 3pi+ 2040 Robot"

    # The 3pi+ robot uses a locally-mounted FAT filesystem.
    # Disable "remote" file access to prevent confusion.
    def supports_remote_directories(self):
        return False

    def supports_remote_files(self):
        return False

class Pololu3pi2040RobotBackendConfigPage(RP2040BackendConfigPage):
    pass

def load_plugin():
    add_micropython_backend(
        "Pololu3pi2040Robot",
        Pololu3pi2040RobotBackendProxy,
        "MicroPython (Pololu 3pi+ 2040 Robot)",
        Pololu3pi2040RobotBackendConfigPage,
        bare_metal=True,
        sort_key="32",
        validate_time=False,
        sync_time=True,
        submit_mode=RAW_PASTE_SUBMIT_MODE,
        write_block_size=64,
    )

    # Don't consider Pico in generic backends
    # The main reason is to reduce the number of items in the backend switcher menu
    import thonny.plugins.circuitpython
    import thonny.plugins.esp
    import thonny.plugins.micropython
    import thonny.plugins.rp2040

    thonny.plugins.circuitpython.cirpy_front.VIDS_PIDS_TO_AVOID.update(
        Pololu3pi2040RobotBackendProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.micropython.mp_front.VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        Pololu3pi2040RobotBackendProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.esp.VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS.update(
        Pololu3pi2040RobotBackendProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.rp2040.VIDS_PIDS_TO_AVOID_IN_RP2040.update(
        Pololu3pi2040RobotBackendProxy.get_known_usb_vids_pids()
    )
