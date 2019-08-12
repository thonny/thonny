import os.path
import tkinter as tk
from tkinter import ttk

from thonny.plugins.micropython import (
    MicroPythonProxy,
    MicroPythonConfigPage,
    add_micropython_backend,
)
from thonny import get_workbench
from thonny.ui_utils import create_url_label, show_dialog, askopenfilename
import threading
from tkinter.messagebox import showinfo
from thonny.misc_utils import list_volumes


class CircuitPythonProxy(MicroPythonProxy):
    @property
    def known_usb_vids_pids(self):
        """Copied from https://github.com/mu-editor/mu/blob/master/mu/modes/adafruit.py"""
        return {
            (0x239A, 0x8015),  # Adafruit Feather M0 CircuitPython
            (0x239A, 0x8023),  # Adafruit Feather M0 Express CircuitPython
            (0x239A, 0x801B),  # Adafruit Feather M0 Express CircuitPython
            (0x239A, 0x8014),  # Adafruit Metro M0 CircuitPython
            (0x239A, 0x8019),  # Adafruit CircuitPlayground Express CircuitPython
            (0x239A, 0x801D),  # Adafruit Gemma M0
            (0x239A, 0x801F),  # Adafruit Trinket M0
            (0x239A, 0x8012),  # Adafruit ItsyBitsy M0
            (0x239A, 0x8021),  # Adafruit Metro M4
            (0x239A, 0x8025),  # Adafruit Feather RadioFruit
            (0x239A, 0x8026),  # Adafruit Feather M4
            (0x239A, 0x8028),  # Adafruit pIRKey M0
            (0x239A, 0x802A),  # Adafruit Feather 52840
            (0x239A, 0x802C),  # Adafruit Itsy M4
            (0x239A, 0x802E),  # Adafruit CRICKit M0
        }


class CircuitPythonConfigPage(MicroPythonConfigPage):
    def _get_usb_driver_url(self):
        return "https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython"


def load_plugin():
    add_micropython_backend(
        "CircuitPython", CircuitPythonProxy, _("CircuitPython (generic)"), CircuitPythonConfigPage
    )
