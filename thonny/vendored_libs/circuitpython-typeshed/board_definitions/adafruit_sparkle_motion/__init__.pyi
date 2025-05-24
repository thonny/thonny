# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Sparkle Motion
 - port: espressif
 - board_id: adafruit_sparkle_motion
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IR: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
NEOPIXEL: microcontroller.Pin  # GPIO2
LED: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
SIG1: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
SIG2: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
SIG3: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
BOOT: microcontroller.Pin  # GPIO0
BUTTON: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
A0: microcontroller.Pin  # GPIO27
D27: microcontroller.Pin  # GPIO27
SCL: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
RX: microcontroller.Pin  # GPIO10
D10: microcontroller.Pin  # GPIO10
SIG4: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
TX: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
D18: microcontroller.Pin  # GPIO18


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
