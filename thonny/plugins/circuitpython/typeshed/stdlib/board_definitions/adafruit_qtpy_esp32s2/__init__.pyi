# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit QT Py ESP32S2
 - port: espressif
 - board_id: adafruit_qtpy_esp32s2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
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
A0: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
A1: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
A2: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
A3: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
SDA: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
A4: microcontroller.Pin  # GPIO7
SCL: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
A5: microcontroller.Pin  # GPIO6
TX: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
A6: microcontroller.Pin  # GPIO5
RX: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
A7: microcontroller.Pin  # GPIO16
MOSI: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
SCK: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
MISO: microcontroller.Pin  # GPIO37
D37: microcontroller.Pin  # GPIO37
NEOPIXEL_POWER: microcontroller.Pin  # GPIO38
NEOPIXEL: microcontroller.Pin  # GPIO39
SCL1: microcontroller.Pin  # GPIO40
D40: microcontroller.Pin  # GPIO40
SDA1: microcontroller.Pin  # GPIO41
D41: microcontroller.Pin  # GPIO41


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
