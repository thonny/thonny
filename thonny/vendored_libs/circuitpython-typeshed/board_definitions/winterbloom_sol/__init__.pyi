# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Winterbloom Sol
 - port: atmel-samd
 - board_id: winterbloom_sol
 - NVM size: 256
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, alarm, analogio, array, atexit, binascii, bitbangio, board, builtins, builtins.pow3, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, errno, floppyio, frequencyio, getpass, io, json, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, sys, time, traceback, ulab, usb, usb_cdc, usb_midi, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SCK: microcontroller.Pin  # PA17
MOSI: microcontroller.Pin  # PB23
MISO: microcontroller.Pin  # PB22
DAC_CS: microcontroller.Pin  # PA18
G1: microcontroller.Pin  # PA20
G2: microcontroller.Pin  # PA21
G3: microcontroller.Pin  # PA22
G4: microcontroller.Pin  # PA23
NEOPIXEL: microcontroller.Pin  # PB03


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
