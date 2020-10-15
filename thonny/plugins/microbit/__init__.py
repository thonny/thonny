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
    def get_missing_device_text(self):
        return "Can't see your micro:bit..."

    def get_instructions(self) -> Optional[str]:
        return (
            "NB! Installing new firmware will erase all files you may have on your micro:bit!\n\n"
            "1. Plug in your micro:bit\n"
            "2. Wait until 'Target location' shows your micro:bit location\n"
            "3. Press 'Install'\n"
            "4. Wait until the latest firmware is downloaded and copied onto your device\n"
            "5. Close the dialog and choose 'MicroPython (BBC micro:bit)' interpreter"
        )

    def _get_release_info_url(self):
        return "https://api.github.com/repos/bbcmicrobit/micropython/releases/latest"

    def _is_suitable_asset(self, asset, model_id):
        if not asset["name"].endswith(".hex") or "micropython" not in asset["name"].lower():
            return False

        # https://tech.microbit.org/latest-revision/editors/
        if model_id in ("9900", "9901"):
            return 400000 < asset["size"] < 800000
        elif model_id in ("9904"):
            return 1100000 < asset["size"] < 2000000
        else:
            return False

    def get_target_dirs(self):
        return [
            vol
            for vol in list_volumes(skip_letters=["A"])
            if os.path.exists(os.path.join(vol, "MICROBIT.HTM"))
        ]

    def _find_device_id(self, mount_path):
        info_path = os.path.join(mount_path, "DETAILS.TXT")
        assert os.path.isfile(info_path)

        # https://tech.microbit.org/latest-revision/editors/
        with open(info_path, "r", encoding="UTF-8", errors="replace") as fp:
            id_marker = "Unique ID:"
            for line in fp:
                if line.startswith(id_marker):
                    unique_id = line[len(id_marker) :].strip()
                    return unique_id[:4]

    def get_title(self):
        return "Install MicroPython firmware for BBC micro:bit"


def load_plugin():
    add_micropython_backend(
        "microbit",
        MicrobitProxy,
        "MicroPython (BBC micro:bit)",
        MicrobitConfigPage,
        sort_key="31",
        validate_time=False,
        sync_time=False,
    )
