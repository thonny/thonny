from logging import getLogger
from typing import List

from thonny.plugins.micropython import add_micropython_backend
from thonny.plugins.micropython.mp_common import RAW_PASTE_SUBMIT_MODE
from thonny.plugins.micropython.mp_front import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    get_uart_adapter_vids_pids,
)
from thonny.plugins.micropython.uf2dialog import show_uf2_installer

logger = getLogger(__name__)

VIDS_PIDS_TO_AVOID_IN_RP2040 = set()


class RP2040BackendProxy(BareMetalMicroPythonProxy):
    @classmethod
    def should_consider_unknown_devices(cls):
        return True

    @classmethod
    def get_known_usb_vids_pids(cls):
        # can be anything
        return set()

    def get_node_label(self):
        return "RP2040 device"

    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.rp2040.rp2040_back

        return thonny.plugins.rp2040.rp2040_back.__file__

    @classmethod
    def get_vids_pids_to_avoid(self):
        return get_uart_adapter_vids_pids() | VIDS_PIDS_TO_AVOID_IN_RP2040


class RP2040BackendConfigPage(BareMetalMicroPythonConfigPage):
    def get_flashing_dialog_kinds(self) -> List[str]:
        return [""]

    def _open_flashing_dialog(self, kind: str) -> None:
        assert kind == ""
        show_uf2_installer(self, firmware_name="MicroPython")

    @property
    def allow_webrepl(self):
        return True


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
