# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Espressif ESP32-LyraT
 - port: espressif
 - board_id: espressif_esp32_lyrat
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
CS0: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
MISO: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
MOSI: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
SCK: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
TX: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
SCL: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
SDA: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
D0: microcontroller.Pin  # GPIO0
D5: microcontroller.Pin  # GPIO5
D25: microcontroller.Pin  # GPIO25
D26: microcontroller.Pin  # GPIO26
D35: microcontroller.Pin  # GPIO35
LED: microcontroller.Pin  # GPIO22
L: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
BUTTON: microcontroller.Pin  # GPIO36
REC: microcontroller.Pin  # GPIO36
SW36: microcontroller.Pin  # GPIO36
BUTTON: microcontroller.Pin  # GPIO39
MODE: microcontroller.Pin  # GPIO39
SW39: microcontroller.Pin  # GPIO39


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
