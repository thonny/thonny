# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for uGame10
 - port: atmel-samd
 - board_id: ugame10
 - NVM size: 256
 - Included modules: _stage, analogio, array, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, nvm, onewireio, os, pwmio, rainbowio, random, rotaryio, storage, struct, supervisor, sys, terminalio, time, usb_cdc, warnings
 - Frozen libraries: stage, ugame
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
X: microcontroller.Pin  # PA00
O: microcontroller.Pin  # PA01
SPEAKER: microcontroller.Pin  # PA02
MUTE: microcontroller.Pin  # PA23
BATTERY: microcontroller.Pin  # PA10
UP: microcontroller.Pin  # PA03
LEFT: microcontroller.Pin  # PA04
DOWN: microcontroller.Pin  # PA22
RIGHT: microcontroller.Pin  # PA05
MOSI: microcontroller.Pin  # PA06
SCK: microcontroller.Pin  # PA07
DC: microcontroller.Pin  # PA09
CS: microcontroller.Pin  # PA08
A: microcontroller.Pin  # PA11
B: microcontroller.Pin  # PA14
C: microcontroller.Pin  # PA15
D: microcontroller.Pin  # PA28


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
