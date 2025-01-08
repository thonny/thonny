# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Espressif ESP32 TTGO T8 v1.7
 - port: espressif
 - board_id: ttgo_t8_v1_7
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
I36: microcontroller.Pin  # GPIO36
VP: microcontroller.Pin  # GPIO36
I39: microcontroller.Pin  # GPIO39
VN: microcontroller.Pin  # GPIO39
I34: microcontroller.Pin  # GPIO34
I35: microcontroller.Pin  # GPIO35
IO32: microcontroller.Pin  # GPIO32
IO33: microcontroller.Pin  # GPIO33
IO25: microcontroller.Pin  # GPIO25
IO26: microcontroller.Pin  # GPIO26
IO27: microcontroller.Pin  # GPIO27
IO14: microcontroller.Pin  # GPIO14
SD_SCK: microcontroller.Pin  # GPIO14
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
SD_CS: microcontroller.Pin  # GPIO13
IO15: microcontroller.Pin  # GPIO15
SD_MOSI: microcontroller.Pin  # GPIO15
LED: microcontroller.Pin  # GPIO21
SDA: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21
IO1: microcontroller.Pin  # GPIO1
TX: microcontroller.Pin  # GPIO1
IO3: microcontroller.Pin  # GPIO3
RX: microcontroller.Pin  # GPIO3
IO22: microcontroller.Pin  # GPIO22
SCL: microcontroller.Pin  # GPIO22
IO19: microcontroller.Pin  # GPIO19
IO23: microcontroller.Pin  # GPIO23
IO18: microcontroller.Pin  # GPIO18
IO5: microcontroller.Pin  # GPIO5
SD_MISO: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO2
IO0: microcontroller.Pin  # GPIO0
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
IO4: microcontroller.Pin  # GPIO4


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
