# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for cezerio dev ESP32C6
 - port: espressif
 - board_id: cezerio_dev_ESP32C6
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
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
NEOPIXEL: microcontroller.Pin  # GPIO3
RGB: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
SCL: microcontroller.Pin  # GPIO7
IMUSC: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
SDA: microcontroller.Pin  # GPIO8
IMUSD: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
BUTTON: microcontroller.Pin  # GPIO9
BOOT: microcontroller.Pin  # GPIO9
IO14: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
SS: microcontroller.Pin  # GPIO14
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
NEOPIXEL_MATRIX: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
D20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
SCK: microcontroller.Pin  # GPIO21
IO22: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
MOSI: microcontroller.Pin  # GPIO22
MO: microcontroller.Pin  # GPIO22
IO23: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO23
MI: microcontroller.Pin  # GPIO23


# Members:
def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

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
