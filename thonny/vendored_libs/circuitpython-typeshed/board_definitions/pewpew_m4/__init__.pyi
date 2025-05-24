# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PewPew M4
 - port: atmel-samd
 - board_id: pewpew_m4
 - NVM size: 256
 - Included modules: _stage, array, audiocore, audioio, audiomixer, board, builtins, busdisplay, busio, busio.SPI, busio.UART, collections, digitalio, displayio, epaperdisplay, fontio, fourwire, i2cdisplaybus, keypad, keypad.Keys, math, microcontroller, nvm, os, random, spitarget, storage, struct, supervisor, sys, terminalio, tilepalettemapper, time, usb_cdc, zlib
 - Frozen libraries: pew, stage, ugame
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON_LEFT: microcontroller.Pin  # PB23
BUTTON_RIGHT: microcontroller.Pin  # PB22
BUTTON_UP: microcontroller.Pin  # PA23
BUTTON_DOWN: microcontroller.Pin  # PA27
BUTTON_O: microcontroller.Pin  # PA10
BUTTON_X: microcontroller.Pin  # PA09
BUTTON_Z: microcontroller.Pin  # PA22
P1: microcontroller.Pin  # PA30
P2: microcontroller.Pin  # PA31
P3: microcontroller.Pin  # PA00
P4: microcontroller.Pin  # PA01
P5: microcontroller.Pin  # PA02
P6: microcontroller.Pin  # PA04
P7: microcontroller.Pin  # PA05
TFT_RST: microcontroller.Pin  # PA17
TFT_DC: microcontroller.Pin  # PA16
TFT_MOSI: microcontroller.Pin  # PA15
TFT_SCK: microcontroller.Pin  # PA13
TFT_CS: microcontroller.Pin  # PA11
SPEAKER: microcontroller.Pin  # PA02
SDA: microcontroller.Pin  # PA00
SCL: microcontroller.Pin  # PA01
SCK: microcontroller.Pin  # PA04
MOSI: microcontroller.Pin  # PA05
MISO: microcontroller.Pin  # PA00
TX: microcontroller.Pin  # PA05
RX: microcontroller.Pin  # PA00


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
