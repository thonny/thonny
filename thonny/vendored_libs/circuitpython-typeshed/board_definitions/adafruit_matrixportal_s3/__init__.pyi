# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit MatrixPortal S3
 - port: espressif
 - board_id: adafruit_matrixportal_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Dict, Tuple


# Board Info:
board_id: str


# Pins:
clock_pin: microcontroller.Pin  # GPIO2
latch_pin: microcontroller.Pin  # GPIO47
output_enable_pin: microcontroller.Pin  # GPIO14
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
SDA: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
LED: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
L: microcontroller.Pin  # GPIO13
A4: microcontroller.Pin  # GPIO11
A3: microcontroller.Pin  # GPIO10
A2: microcontroller.Pin  # GPIO9
A1: microcontroller.Pin  # GPIO3
A0: microcontroller.Pin  # GPIO12
NEOPIXEL: microcontroller.Pin  # GPIO4
RX: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
TX: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
MTX_R1: microcontroller.Pin  # GPIO42
MTX_G1: microcontroller.Pin  # GPIO41
MTX_B1: microcontroller.Pin  # GPIO40
MTX_R2: microcontroller.Pin  # GPIO38
MTX_G2: microcontroller.Pin  # GPIO39
MTX_B2: microcontroller.Pin  # GPIO37
MTX_ADDRA: microcontroller.Pin  # GPIO45
MTX_ADDRB: microcontroller.Pin  # GPIO36
MTX_ADDRC: microcontroller.Pin  # GPIO48
MTX_ADDRD: microcontroller.Pin  # GPIO35
MTX_ADDRE: microcontroller.Pin  # GPIO21
MTX_CLK: microcontroller.Pin  # GPIO2
MTX_LAT: microcontroller.Pin  # GPIO47
MTX_OE: microcontroller.Pin  # GPIO14
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # GPIO15
BUTTON_UP: microcontroller.Pin  # GPIO6
BUTTON_DOWN: microcontroller.Pin  # GPIO7


# Members:
rgb_pins: Tuple[Any]

MTX_ADDRESS: Tuple[Any]

MTX_COMMON: Dict[str, Any]

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
