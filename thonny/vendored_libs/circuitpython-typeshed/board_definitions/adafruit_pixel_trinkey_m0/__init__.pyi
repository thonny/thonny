# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Pixel Trinkey M0
 - port: atmel-samd
 - board_id: adafruit_pixel_trinkey_m0
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pulseio, pwmio, rainbowio, random, storage, struct, supervisor, sys, time, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_dotstar, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
NEOPIXEL: microcontroller.Pin  # PA01
VOLTAGE_MONITOR: microcontroller.Pin  # PA02
D4: microcontroller.Pin  # PA06
MISO: microcontroller.Pin  # PA06
DATA: microcontroller.Pin  # PA04
MOSI: microcontroller.Pin  # PA04
CLOCK: microcontroller.Pin  # PA05
SCK: microcontroller.Pin  # PA05


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
