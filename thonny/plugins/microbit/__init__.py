import os.path
import sys
import threading
from time import sleep
from tkinter import messagebox, ttk
from typing import Optional

from thonny import get_workbench, ui_utils
from thonny.languages import tr
from thonny.misc_utils import find_volume_by_name, list_volumes
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
)
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog
from thonny.ui_utils import CommonDialog, FileCopyDialog, ems_to_pixels

LATEST_RELEASE_URL = "https://api.github.com/repos/bbcmicrobit/micropython/releases/latest"


class MicrobitProxy(BareMetalMicroPythonProxy):
    def _start_background_process(self, clean=None, extra_args=[]):
        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies
        # https://github.com/pyserial/pyserial/issues/176
        # In my Sierra, Calliope and micro:bit seemed to soft-reboot
        # when reconnected too quickly.

        if clean and sys.platform == "darwin":
            sleep(1.0)

        super()._start_background_process(clean)

    def supports_remote_directories(self):
        return False

    @classmethod
    def should_consider_unknown_devices(cls):
        return False

    @classmethod
    def get_known_usb_vids_pids(self):
        return {(0x0D28, 0x0204)}


class MicrobitConfigPage(BareMetalMicroPythonConfigPage):
    def _get_usb_driver_url(self):
        return "https://microbit-micropython.readthedocs.io/en/latest/devguide/repl.html"

    def _get_intro_text(self):
        return (
            super()._get_intro_text()
            + "\n\n"
            + tr("Make sure MicroPython has been installed to your micro:bit.")
            + "\n("
            + tr("Don't forget that main.py only works without embedded main script.")
            + ")"
        )

    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = MicrobitFlashingDialog(self)
        ui_utils.show_dialog(dlg)


class MicrobitFlashingDialog(Uf2FlashingDialog):
    def get_instructions(self) -> Optional[str]:
        return (
            "This dialog allows you to install or update MicroPython firmware on your micro:bit.\n"
            "\n"
            "1. Plug in your micro:bit.\n"
            "2. Wait until device information appears.\n"
            "3. Click 'Install' and wait for some seconds until done.\n"
            "4. Close the dialog and start programming!\n"
            "\n"
            "NB! Installing a new firmware will erase all files you may have on your\n"
            "device. Make sure you have important files backed up!"
        )

    def _get_release_info_url(self):
        return "https://raw.githubusercontent.com/thonny/thonny/master/data/microbit-firmware.json"

    def get_unknown_version_text(self):
        return "?"

    def get_firmware_description(self):
        info = self._get_latest_firmware_info_for_current_device()
        if info is None:
            return None
        return "%s (%s)" % (info["version"], info["date"])

    def _get_latest_firmware_info_for_current_device(self):
        if self._possible_targets is None or len(self._possible_targets) != 1:
            return None
        else:
            board_id = self._possible_targets[0][1]
            return self._get_latest_firmware_info_for_device(board_id)

    def _get_latest_firmware_info_for_device(self, board_id):
        if self._release_info is None:
            return None
        else:
            return self._release_info["latest_firmwares"].get(board_id, None)

    def get_download_url_and_size(self, board_id):
        info = self._get_latest_firmware_info_for_device(board_id)
        if info is None:
            return None

        return info["hex_download"], info["size"]

    def get_target_filename(self):
        return "firmware.hex"

    @classmethod
    def find_device_board_id_and_model(cls, mount_path):
        info_path = os.path.join(mount_path, "DETAILS.TXT")
        if not os.path.isfile(info_path):
            return None

        # https://tech.microbit.org/latest-revision/editors/
        models = {
            "9900": "BBC micro:bit v1.3",
            "9901": "BBC micro:bit v1.5",
            "9903": "BBC micro:bit v2.0 (9903)",
            "9904": "BBC micro:bit v2.0",
        }

        with open(info_path, "r", encoding="UTF-8", errors="replace") as fp:
            id_marker = "Unique ID:"
            for line in fp:
                if line.startswith(id_marker):
                    board_id = line[len(id_marker) :].strip()[:4]
                    if board_id in models:
                        return board_id, models[board_id]

            # With older bootloaders, the file may be different
            fp.seek(0)
            for line in fp:
                if "Version: 0234" in line:
                    board_id = "9900"
                    return board_id, models[board_id]

        return None

    def get_title(self):
        return "Install MicroPython firmware for BBC micro:bit"

    def _get_vid_pids_to_wait_for(self):
        return MicrobitProxy.get_known_usb_vids_pids()


def load_plugin():
    add_micropython_backend(
        "microbit",
        MicrobitProxy,
        "MicroPython (BBC micro:bit)",
        MicrobitConfigPage,
        sort_key="31",
        validate_time=False,
        sync_time=False,
        write_block_size=128,
    )

    # Don't consider micro:bit in generic backends
    # The main reason is to reduce the number of items in the backend switcher menu
    import thonny.plugins.circuitpython
    import thonny.plugins.micropython

    thonny.plugins.circuitpython.VIDS_PIDS_TO_AVOID.update(MicrobitProxy.get_known_usb_vids_pids())
    thonny.plugins.micropython.VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
