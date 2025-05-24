# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Electronic Cats Hunter Cat NFC
 - port: atmel-samd
 - board_id: huntercat_nfc
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA03
D0: microcontroller.Pin  # PA00
LED: microcontroller.Pin  # PA00
D1: microcontroller.Pin  # PA01
D2: microcontroller.Pin  # PA02
D3: microcontroller.Pin  # PA03
D8: microcontroller.Pin  # PA08
D9: microcontroller.Pin  # PA09
D10: microcontroller.Pin  # PA10
D11: microcontroller.Pin  # PA11
D14: microcontroller.Pin  # PA14
D15: microcontroller.Pin  # PA15
D16: microcontroller.Pin  # PA16
D17: microcontroller.Pin  # PA17
D18: microcontroller.Pin  # PA18
D19: microcontroller.Pin  # PA19
D22: microcontroller.Pin  # PA22
D27: microcontroller.Pin  # PA27
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09
SCK: microcontroller.Pin  # PA19
MOSI: microcontroller.Pin  # PA18
MISO: microcontroller.Pin  # PA22


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
