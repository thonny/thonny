import logging
import os.path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from typing import Optional

from thonny import get_workbench, ui_utils
from thonny.languages import tr
from thonny.misc_utils import list_volumes
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
)
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog
from thonny.ui_utils import askopenfilename, create_url_label, show_dialog

logger = logging.getLogger(__name__)

VIDS_PIDS_TO_AVOID = set()


class CircuitPythonProxy(BareMetalMicroPythonProxy):
    @classmethod
    def get_known_usb_vids_pids(cls):
        """Information gathered from
        https://github.com/mu-editor/mu/blob/master/mu/modes/circuitpython.py
        https://github.com/microsoft/uf2-samdx1
        """
        return {
            (0x03EB, 0x2402),  # Generic Corp., SAMD21 or SAME54 Board
            (0x04D8, 0xEC72),  # XinaBox CC03
            (0x04D8, 0xEC75),  # XinaBox CS11
            (0x04D8, 0xED94),  # PyCubed
            (0x04D8, 0xED5E),  # XinaBox CW03
            (0x04D8, 0xEDB3),  # Capable Robot Components, Programmable USB Hub
            (0x04D8, 0xEDBE),  # maholli, SAM32
            (0x04D8, 0xEF66),  # eduSense, senseBox MCU
            (0x1209, 0x2017),  # Benjamin Shockley, Mini SAM M4
            (0x1209, 0x4D44),  # Robotics Masters, Robo HAT MM1 M4
            (0x1209, 0x7102),  # Mini SAM M0
            (0x1209, 0xBAB1),  # Electronic Cats Meow Meow
            (0x1209, 0xBAB2),  # Electronic Cats CatWAN USBStick
            (0x1209, 0xBAB3),  # Electronic Cats Bast Pro Mini M0
            (0x1209, 0xBAB6),  # Electronic Cats Escornabot Makech
            (0x16D0, 0x0CDA),  # dadamachines, automat
            (0x1B4F, 0x0016),  # Sparkfun Thing Plus - SAMD51
            (0x1B4F, 0x8D22),  # SparkFun SAMD21 Mini Breakout
            (0x1B4F, 0x8D23),  # SparkFun SAMD21 Dev Breakout
            (0x1D50, 0x60E8),  # PewPew Game Console
            (0x1D50, 0x6110),  # Eitech, Robotics
            (0x1D50, 0x6112),  # Watterott electronic, Wattuino RC
            (0x2341, 0x8053),  # Arduino LLC, Arduino MKR1300
            (0x2341, 0x8057),  # Arduino Nano 33 IoT board
            (0x239A, None),  # Adafruit
            (0x2886, 0x802D),  # Seeed Wio Terminal
            (0x2886, 0x000D),  # Seeed Studio, Grove Zero
            (0x2B04, 0xC00C),  # Particle Argon
            (0x2B04, 0xC00D),  # Particle Boron
            (0x2B04, 0xC00E),  # Particle Xenon
            (0x3171, 0x0101),  # 8086.net Commander
        }

    @classmethod
    def get_vids_pids_to_avoid(self):
        return VIDS_PIDS_TO_AVOID


class CircuitPythonConfigPage(BareMetalMicroPythonConfigPage):
    def _get_usb_driver_url(self):
        return "https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython"

    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = CircuitPythonFlashingDialog(self)
        ui_utils.show_dialog(dlg)


class CircuitPythonFlashingDialog(Uf2FlashingDialog):
    def __init__(self, master):
        self._devices_info = {}
        super(CircuitPythonFlashingDialog, self).__init__(master)

    def get_instructions(self) -> Optional[str]:
        return (
            "This dialog allows you to install or update CircuitPython firmware on your device.\n"
            "\n"
            "1. Plug in your device into bootloader mode by double-pressing the reset button.\n"
            "2. Wait until device information appears.\n"
            "3. (If nothing happens in 10 seconds, then try shorter or longer pauses between presses.)\n"
            "4. Click 'Install' and wait until done.\n"
            "5. Close the dialog and start programming!"
        )

    def _get_release_info_url(self):
        return "https://api.github.com/repos/adafruit/circuitpython/releases/latest"

    def _get_devices_info_url(self):
        # use the master version, not bundled version
        return "https://raw.githubusercontent.com/thonny/thonny/master/thonny/plugins/circuitpython/devices.json"

    def _download_release_info(self):
        # First download devices
        import json
        from urllib.request import urlopen

        try:
            with urlopen(self._get_devices_info_url()) as fp:
                self._devices_info = json.loads(fp.read().decode("UTF-8"))
        except Exception as e:
            logger.warning(
                "Could not find release info from %s", self._get_release_info_url(), exc_info=e
            )
            return

        # ... and then release
        super(CircuitPythonFlashingDialog, self)._download_release_info()

    def get_download_url_and_size(self, board_id):
        # TODO: should take vid/pid also into account. It looks like different models may have same board_id
        if self._release_info is None or self._devices_info is None:
            return None

        if not "tag_name" in self._release_info:
            raise RuntimeError("Could not find tag_name from %s" % self._get_release_info_url())

        release = self._release_info["tag_name"]

        if not self._devices_info.get(board_id, {}).get("FIRMWARE_DOWNLOAD", None):
            raise RuntimeError(
                "Could not find your board (%s) or its download url from %s (consider making a PR). "
                % (board_id, self._get_devices_info_url())
                + "Please find the firmware from https://circuitpython.org/ and install it manually."
            )

        url = self._devices_info[board_id]["FIRMWARE_DOWNLOAD"].format(
            lang="en_US", release=release
        )

        # reporting approximate size for now. Downloader can take precise value from the header later
        size = 2 ** 20  # 1 MiB
        return (url, size)

    def _is_suitable_asset(self, asset, model_id):
        # not used here
        return False

    def get_title(self):
        return "Install CircuitPython firmware for your device"

    def _get_vid_pids_to_wait_for(self):
        return CircuitPythonProxy.get_known_usb_vids_pids()


def load_plugin():
    add_micropython_backend(
        "CircuitPython",
        CircuitPythonProxy,
        tr("CircuitPython (generic)"),
        CircuitPythonConfigPage,
        sort_key="50",
    )
