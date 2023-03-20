import sys
from logging import getLogger
from typing import List

from thonny import ui_utils
from thonny.languages import tr
from thonny.plugins.microbit import MicrobitFlashingDialog
from thonny.plugins.micropython.esptool_dialog import try_launch_esptool_dialog
from thonny.plugins.micropython.mp_front import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
)
from thonny.plugins.micropython.uf2dialog import show_uf2_installer

logger = getLogger(__name__)

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

    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.circuitpython.cirpy_back

        return thonny.plugins.circuitpython.cirpy_back.__file__

    @classmethod
    def _is_for_micropython(cls):
        return False

    @classmethod
    def _is_for_circuitpython(cls):
        return True

    @classmethod
    def _is_potential_port(cls, p):
        # micro:bit's v2's CircuitPython does not have CircuitPython's port attributes
        if (p.vid, p.pid) == (0x0D28, 0x0204):
            return True

        if "adafruit_board_toolkit" in sys.modules or sys.platform == "linux":
            # can trust p.interface value
            return "CircuitPython CDC " in (p.interface or "")
        else:
            return super()._is_potential_port(p)


class CircuitPythonConfigPage(BareMetalMicroPythonConfigPage):
    def _get_intro_url(self):
        return "https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython"

    def get_flashing_dialog_kinds(self) -> List[str]:
        return ["UF2", "esptool", "BBC micro:bit"]

    def _open_flashing_dialog(self, kind: str) -> None:
        if kind == "UF2":
            show_uf2_installer(self, firmware_name="CircuitPython")
        elif kind == "esptool":
            try_launch_esptool_dialog(self.winfo_toplevel(), "CircuitPython")
        elif kind == "BBC micro:bit":
            dlg = MicrobitFlashingDialog(self, "CircuitPython")
            ui_utils.show_dialog(dlg)

    def _get_flasher_link_title(self) -> str:
        return tr("Install or update %s") % "CircuitPython"
