# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5STACK STAMP-C3
 - port: espressif
 - board_id: m5stack_stamp_c3
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
G0: microcontroller.Pin  # GPIO0
IO0: microcontroller.Pin  # GPIO0
G1: microcontroller.Pin  # GPIO1
IO1: microcontroller.Pin  # GPIO1
NEOPIXEL: microcontroller.Pin  # GPIO2
G2: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO2
BUTTON: microcontroller.Pin  # GPIO3
G3: microcontroller.Pin  # GPIO3
IO3: microcontroller.Pin  # GPIO3
G4: microcontroller.Pin  # GPIO4
IO4: microcontroller.Pin  # GPIO4
G5: microcontroller.Pin  # GPIO5
IO5: microcontroller.Pin  # GPIO5
G6: microcontroller.Pin  # GPIO6
IO6: microcontroller.Pin  # GPIO6
G7: microcontroller.Pin  # GPIO7
IO7: microcontroller.Pin  # GPIO7
G8: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
G9: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
G10: microcontroller.Pin  # GPIO10
IO10: microcontroller.Pin  # GPIO10
G18: microcontroller.Pin  # GPIO18
IO18: microcontroller.Pin  # GPIO18
G19: microcontroller.Pin  # GPIO19
IO19: microcontroller.Pin  # GPIO19
RX: microcontroller.Pin  # GPIO20
G20: microcontroller.Pin  # GPIO20
IO20: microcontroller.Pin  # GPIO20
TX: microcontroller.Pin  # GPIO21
G21: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
