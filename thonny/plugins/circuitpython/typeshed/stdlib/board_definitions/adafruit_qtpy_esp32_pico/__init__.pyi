# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit QT Py ESP32 PICO
 - port: espressif
 - board_id: adafruit_qtpy_esp32_pico
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
A0: microcontroller.Pin  # GPIO26
D18: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO25
D17: microcontroller.Pin  # GPIO25
A2: microcontroller.Pin  # GPIO27
D9: microcontroller.Pin  # GPIO27
A3: microcontroller.Pin  # GPIO15
D8: microcontroller.Pin  # GPIO15
SDA: microcontroller.Pin  # GPIO4
D7: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO33
D6: microcontroller.Pin  # GPIO33
A5: microcontroller.Pin  # GPIO33
TX: microcontroller.Pin  # GPIO32
D5: microcontroller.Pin  # GPIO32
A6: microcontroller.Pin  # GPIO32
RX: microcontroller.Pin  # GPIO7
D16: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO7
MOSI: microcontroller.Pin  # GPIO13
D35: microcontroller.Pin  # GPIO13
SCK: microcontroller.Pin  # GPIO14
D36: microcontroller.Pin  # GPIO14
MISO: microcontroller.Pin  # GPIO12
D37: microcontroller.Pin  # GPIO12
NEOPIXEL_POWER: microcontroller.Pin  # GPIO8
NEOPIXEL: microcontroller.Pin  # GPIO5
SCL1: microcontroller.Pin  # GPIO19
D40: microcontroller.Pin  # GPIO19
SDA1: microcontroller.Pin  # GPIO22
D41: microcontroller.Pin  # GPIO22


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
