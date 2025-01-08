# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit ItsyBitsy ESP32
 - port: espressif
 - board_id: adafruit_itsybitsy_esp32
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO25
A1: microcontroller.Pin  # GPIO26
A2: microcontroller.Pin  # GPIO4
A3: microcontroller.Pin  # GPIO38
A4: microcontroller.Pin  # GPIO37
A5: microcontroller.Pin  # GPIO36
SCK: microcontroller.Pin  # GPIO19
MOSI: microcontroller.Pin  # GPIO21
MISO: microcontroller.Pin  # GPIO22
RX: microcontroller.Pin  # GPIO8
TX: microcontroller.Pin  # GPIO20
SDA: microcontroller.Pin  # GPIO15
SCL: microcontroller.Pin  # GPIO27
D12: microcontroller.Pin  # GPIO12
D14: microcontroller.Pin  # GPIO14
D33: microcontroller.Pin  # GPIO33
D32: microcontroller.Pin  # GPIO32
D7: microcontroller.Pin  # GPIO7
D5: microcontroller.Pin  # GPIO5
D13: microcontroller.Pin  # GPIO13
LED: microcontroller.Pin  # GPIO13
NEOPIXEL: microcontroller.Pin  # GPIO0
NEOPIXEL_POWER: microcontroller.Pin  # GPIO2
BUTTON: microcontroller.Pin  # GPIO35


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
