from logging import getLogger
from typing import Optional

from thonny.plugins.micropython import (
    BareMetalMicroPythonProxy,
    add_micropython_backend,
    BareMetalMicroPythonConfigPage,
)
from thonny.plugins.micropython.bare_metal_backend import RAW_PASTE_SUBMIT_MODE
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog

logger = getLogger(__name__)


class RP2040BackendProxy(BareMetalMicroPythonProxy):
    @classmethod
    def should_consider_unknown_devices(cls):
        return True

    @classmethod
    def get_known_usb_vids_pids(cls):
        # can be anything
        return set()

    @classmethod
    def device_is_present_in_bootloader_mode(cls):
        return bool(Uf2FlashingDialog.get_possible_targets())

    def get_node_label(self):
        return "RP2040 device"

    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.rp2040.rp2040_backend

        return thonny.plugins.rp2040.rp2040_backend.__file__


class RP2040BackendConfigPage(BareMetalMicroPythonConfigPage):
    def _has_flashing_dialog(self):
        return False


def load_plugin():
    add_micropython_backend(
        "RP2040",
        RP2040BackendProxy,
        "MicroPython (RP2040)",
        RP2040BackendConfigPage,
        bare_metal=True,
        sort_key="33",
        validate_time=False,
        sync_time=True,
        submit_mode=RAW_PASTE_SUBMIT_MODE,
        write_block_size=64,
    )
