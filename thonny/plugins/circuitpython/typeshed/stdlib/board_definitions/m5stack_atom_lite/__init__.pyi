# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Atom Lite
 - port: espressif
 - board_id: m5stack_atom_lite
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
D22: microcontroller.Pin  # GPIO22
MOSI: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
SCK: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
A33: microcontroller.Pin  # GPIO33
IR: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
SCL: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
SDA: microcontroller.Pin  # GPIO25
A25: microcontroller.Pin  # GPIO25
D25: microcontroller.Pin  # GPIO25
DAC1: microcontroller.Pin  # GPIO25
PORTA_SDA: microcontroller.Pin  # GPIO26
A26: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
DAC2: microcontroller.Pin  # GPIO25
PORTA_SCL: microcontroller.Pin  # GPIO32
A32: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
NEOPIXEL: microcontroller.Pin  # GPIO27
BTN: microcontroller.Pin  # GPIO39


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
