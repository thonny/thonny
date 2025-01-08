# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32 Devkit V1
 - port: espressif
 - board_id: doit_esp32_devkit_v1
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
D15: microcontroller.Pin  # GPIO15
D2: microcontroller.Pin  # GPIO2
D4: microcontroller.Pin  # GPIO4
RX2: microcontroller.Pin  # GPIO16
TX2: microcontroller.Pin  # GPIO17
D5: microcontroller.Pin  # GPIO5
D18: microcontroller.Pin  # GPIO18
D19: microcontroller.Pin  # GPIO19
D21: microcontroller.Pin  # GPIO21
RX0: microcontroller.Pin  # GPIO1
TX0: microcontroller.Pin  # GPIO3
D22: microcontroller.Pin  # GPIO22
D23: microcontroller.Pin  # GPIO23
D13: microcontroller.Pin  # GPIO13
D12: microcontroller.Pin  # GPIO12
D14: microcontroller.Pin  # GPIO14
D27: microcontroller.Pin  # GPIO27
D26: microcontroller.Pin  # GPIO26
D25: microcontroller.Pin  # GPIO25
D33: microcontroller.Pin  # GPIO33
D32: microcontroller.Pin  # GPIO32
D35: microcontroller.Pin  # GPIO35
D34: microcontroller.Pin  # GPIO34
VN: microcontroller.Pin  # GPIO39
VP: microcontroller.Pin  # GPIO36
LED: microcontroller.Pin  # GPIO2
SDA: microcontroller.Pin  # GPIO21
SCL: microcontroller.Pin  # GPIO22
SCK: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO19
TX: microcontroller.Pin  # GPIO17
RX: microcontroller.Pin  # GPIO16
D1: microcontroller.Pin  # GPIO1
D3: microcontroller.Pin  # GPIO3
D16: microcontroller.Pin  # GPIO16
D17: microcontroller.Pin  # GPIO17


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
