# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Seeed Studio XIAO ESP32C3
 - port: espressif
 - board_id: seeed_xiao_esp32c3
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO2
A0: microcontroller.Pin  # GPIO2
D1: microcontroller.Pin  # GPIO3
A1: microcontroller.Pin  # GPIO3
D2: microcontroller.Pin  # GPIO4
A2: microcontroller.Pin  # GPIO4
D3: microcontroller.Pin  # GPIO5
A3: microcontroller.Pin  # GPIO5
D4: microcontroller.Pin  # GPIO6
SDA: microcontroller.Pin  # GPIO6
D5: microcontroller.Pin  # GPIO7
SCL: microcontroller.Pin  # GPIO7
D6: microcontroller.Pin  # GPIO21
TX: microcontroller.Pin  # GPIO21
D7: microcontroller.Pin  # GPIO20
RX: microcontroller.Pin  # GPIO20
D8: microcontroller.Pin  # GPIO8
SCK: microcontroller.Pin  # GPIO8
D9: microcontroller.Pin  # GPIO9
MISO: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
MOSI: microcontroller.Pin  # GPIO10


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


# Unmapped:
#   none
