# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for TinyC6
 - port: espressif
 - board_id: unexpectedmaker_tinyc6
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
A0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
SDA: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
SCL: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
IO11: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
IO15: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
TX: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
RX: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
SCK: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
D20: microcontroller.Pin  # GPIO20
MISO: microcontroller.Pin  # GPIO20
MI: microcontroller.Pin  # GPIO20
SDI: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
MOSI: microcontroller.Pin  # GPIO21
MO: microcontroller.Pin  # GPIO21
SDO: microcontroller.Pin  # GPIO21
BATTERY: microcontroller.Pin  # GPIO4
VBAT: microcontroller.Pin  # GPIO4
VBAT_SENSE: microcontroller.Pin  # GPIO4
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO4
VBUS: microcontroller.Pin  # GPIO10
VBUS_SENSE: microcontroller.Pin  # GPIO10
NEOPIXEL_POWER: microcontroller.Pin  # GPIO22
NEOPIXEL: microcontroller.Pin  # GPIO23


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
