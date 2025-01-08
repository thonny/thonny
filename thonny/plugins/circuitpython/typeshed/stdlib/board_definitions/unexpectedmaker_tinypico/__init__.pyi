# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for TinyPICO
 - port: espressif
 - board_id: unexpectedmaker_tinypico
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
IO14: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
A14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
A15: microcontroller.Pin  # GPIO15
IO27: microcontroller.Pin  # GPIO27
D27: microcontroller.Pin  # GPIO27
A27: microcontroller.Pin  # GPIO27
IO26: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
A26: microcontroller.Pin  # GPIO26
DAC2: microcontroller.Pin  # GPIO26
IO25: microcontroller.Pin  # GPIO25
D25: microcontroller.Pin  # GPIO25
A25: microcontroller.Pin  # GPIO25
DAC1: microcontroller.Pin  # GPIO25
IO23: microcontroller.Pin  # GPIO23
MOSI: microcontroller.Pin  # GPIO23
SDO: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
IO19: microcontroller.Pin  # GPIO19
MISO: microcontroller.Pin  # GPIO19
SDI: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
IO18: microcontroller.Pin  # GPIO18
SCK: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
IO5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
SCL: microcontroller.Pin  # GPIO22
IO22: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
SDA: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
IO32: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
A32: microcontroller.Pin  # GPIO32
IO33: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
A33: microcontroller.Pin  # GPIO33
BATTERY: microcontroller.Pin  # GPIO35
VBAT: microcontroller.Pin  # GPIO35
VBAT_SENSE: microcontroller.Pin  # GPIO35
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO35
VBUS: microcontroller.Pin  # GPIO9
VBUS_SENSE: microcontroller.Pin  # GPIO9
APA102_MOSI: microcontroller.Pin  # GPIO2
APA102_SCK: microcontroller.Pin  # GPIO12
APA102_PWR: microcontroller.Pin  # GPIO13


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
