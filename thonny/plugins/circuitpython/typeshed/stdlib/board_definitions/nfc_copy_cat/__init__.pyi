# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Electronic Cats NFC Copy Cat
 - port: atmel-samd
 - board_id: nfc_copy_cat
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, onewireio, os, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D2: microcontroller.Pin  # PA02
D6: microcontroller.Pin  # PA06
D7: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA05
D11: microcontroller.Pin  # PA04
LED: microcontroller.Pin  # PA14
D27: microcontroller.Pin  # PA27
D28: microcontroller.Pin  # PA28
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09
SCK: microcontroller.Pin  # PA17
MOSI: microcontroller.Pin  # PA16
MISO: microcontroller.Pin  # PA19
D18: microcontroller.Pin  # PA18


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
