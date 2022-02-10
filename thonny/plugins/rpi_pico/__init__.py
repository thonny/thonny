from logging import getLogger
from typing import Optional

from thonny import ui_utils, get_workbench
from thonny.plugins.micropython import (
    BareMetalMicroPythonProxy,
    add_micropython_backend,
    BareMetalMicroPythonConfigPage,
)
from thonny.plugins.micropython.bare_metal_backend import RAW_PASTE_SUBMIT_MODE
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog
from thonny.plugins.rp2040 import RP2040BackendProxy, RP2040BackendConfigPage
from thonny.ui_utils import show_dialog

logger = getLogger(__name__)


class RaspberryPiPicoBackendProxy(RP2040BackendProxy):
    @classmethod
    def should_consider_unknown_devices(cls):
        return False

    @classmethod
    def get_known_usb_vids_pids(cls):
        # https://github.com/raspberrypi/usb-pid
        return {(0x2E8A, 0x0005)}

    @classmethod
    def device_is_present_in_bootloader_mode(cls):
        return bool(Uf2FlashingDialog.get_possible_targets())

    def get_node_label(self):
        return "Raspberry Pi Pico"

    def _propose_install_firmware(self):
        dlg = PicoFlashingDialog(get_workbench())
        show_dialog(dlg)
        return dlg.success


class RaspberryPiPicoBackendConfigPage(RP2040BackendConfigPage):
    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = PicoFlashingDialog(self.winfo_toplevel())
        ui_utils.show_dialog(dlg)


class PicoFlashingDialog(Uf2FlashingDialog):
    def get_instructions(self) -> Optional[str]:
        return (
            "Here you can install or update MicroPython firmware on Raspberry Pi Pico.\n"
            "\n"
            "1. Plug in your Pico while holding the BOOTSEL button.\n"
            "2. Wait until device information appears.\n"
            "3. Click 'Install'.\n"
            "\n"
            "When the process finishes, your Pico will be running the latest version of\n"
            "MicroPython. Close the dialog and start programming!"
        )

    def _get_release_info_url(self):
        return "https://raw.githubusercontent.com/thonny/thonny/master/data/rpi-pico-firmware.json"

    def get_download_url_and_size(self, board_id):
        if self._release_info is None:
            return None

        logger.info(
            "Assets from %s: %r", self._get_release_info_url(), self._release_info["assets"]
        )
        candidates = self._release_info["assets"]

        if len(candidates) == 0:
            raise RuntimeError(
                "Could not find the right file from the release info (%s)"
                % self._get_release_info_url()
            )
        else:
            # The json is meant for Thonny, so take the first one for now
            return (candidates[0]["browser_download_url"], candidates[0]["size"])

    @classmethod
    def _is_relevant_board_id(cls, board_id):
        return "RPI" in board_id

    def get_title(self):
        return "Install MicroPython firmware for Raspberry Pi Pico"

    def _get_vid_pids_to_wait_for(self):
        return RaspberryPiPicoBackendProxy.get_known_usb_vids_pids()


def load_plugin():
    add_micropython_backend(
        "RPiPico",
        RaspberryPiPicoBackendProxy,
        "MicroPython (Raspberry Pi Pico)",
        RaspberryPiPicoBackendConfigPage,
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
    import thonny.plugins.micropython
    import thonny.plugins.esp

    thonny.plugins.circuitpython.VIDS_PIDS_TO_AVOID.update(
        RaspberryPiPicoBackendProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.micropython.VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        RaspberryPiPicoBackendProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.esp.VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS.update(
        RaspberryPiPicoBackendProxy.get_known_usb_vids_pids()
    )
