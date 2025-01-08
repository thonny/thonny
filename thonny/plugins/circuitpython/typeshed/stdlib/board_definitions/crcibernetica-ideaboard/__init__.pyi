# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for CRCibernetica IdeaBoard
 - port: espressif
 - board_id: crcibernetica-ideaboard
 - NVM size: 8192
 - Included modules: _asyncio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_motor, adafruit_requests, neopixel, simpleio
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
NEOPIXEL: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
RX: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
TX: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
SCK: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
MISO: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
SDA: microcontroller.Pin  # GPIO21
IO22: microcontroller.Pin  # GPIO22
SCL: microcontroller.Pin  # GPIO22
IO23: microcontroller.Pin  # GPIO23
MOSI: microcontroller.Pin  # GPIO23
IO25: microcontroller.Pin  # GPIO25
IO26: microcontroller.Pin  # GPIO26
IO27: microcontroller.Pin  # GPIO27
IO32: microcontroller.Pin  # GPIO32
IO33: microcontroller.Pin  # GPIO33
IO34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO39: microcontroller.Pin  # GPIO39


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
