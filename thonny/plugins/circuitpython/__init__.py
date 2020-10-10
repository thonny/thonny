import os.path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

from thonny import get_workbench
from thonny.languages import tr
from thonny.misc_utils import list_volumes
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
)
from thonny.ui_utils import askopenfilename, create_url_label, show_dialog


class CircuitPythonProxy(BareMetalMicroPythonProxy):
    @classmethod
    def get_known_usb_vids_pids(cls):
        """Copied from https://github.com/mu-editor/mu/blob/master/mu/modes/circuitpython.py"""
        return {
            (0x239A, None),  # Adafruit
            (0x2B04, 0xC00C),  # Particle Argon
            (0x2B04, 0xC00D),  # Particle Boron
            (0x2B04, 0xC00E),  # Particle Xenon
            (0x1209, 0xBAB1),  # Electronic Cats Meow Meow
            (0x1209, 0xBAB2),  # Electronic Cats CatWAN USBStick
            (0x1209, 0xBAB3),  # Electronic Cats Bast Pro Mini M0
            (0x1209, 0xBAB6),  # Electronic Cats Escornabot Makech
            (0x1B4F, 0x8D22),  # SparkFun SAMD21 Mini Breakout
            (0x1B4F, 0x8D23),  # SparkFun SAMD21 Dev Breakout
            (0x1209, 0x2017),  # Mini SAM M4
            (0x1209, 0x7102),  # Mini SAM M0
            (0x04D8, 0xEC72),  # XinaBox CC03
            (0x04D8, 0xEC75),  # XinaBox CS11
            (0x04D8, 0xED5E),  # XinaBox CW03
            (0x3171, 0x0101),  # 8086.net Commander
            (0x04D8, 0xED94),  # PyCubed
            (0x04D8, 0xEDBE),  # SAM32
            (0x1D50, 0x60E8),  # PewPew Game Console
            (0x2886, 0x802D),  # Seeed Wio Terminal
            (0x1B4F, 0x0016),  # Sparkfun Thing Plus - SAMD51
            (0x2341, 0x8057),  # Arduino Nano 33 IoT board
        }


class CircuitPythonConfigPage(BareMetalMicroPythonConfigPage):
    def _get_usb_driver_url(self):
        return "https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython"


def load_plugin():
    add_micropython_backend(
        "CircuitPython",
        CircuitPythonProxy,
        tr("CircuitPython (generic)"),
        CircuitPythonConfigPage,
        sort_key="50",
    )
