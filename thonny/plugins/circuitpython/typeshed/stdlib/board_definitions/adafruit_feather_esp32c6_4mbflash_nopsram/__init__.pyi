# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather ESP32-C6 4MB Flash No PSRAM
 - port: espressif
 - board_id: adafruit_feather_esp32c6_4mbflash_nopsram
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO1
IO1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO4
IO4: microcontroller.Pin  # GPIO4
A2: microcontroller.Pin  # GPIO6
IO6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
A3: microcontroller.Pin  # GPIO5
IO5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
A4: microcontroller.Pin  # GPIO3
IO3: microcontroller.Pin  # GPIO3
A5: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO2
SCK: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21
MOSI: microcontroller.Pin  # GPIO22
IO22: microcontroller.Pin  # GPIO22
MISO: microcontroller.Pin  # GPIO23
IO23: microcontroller.Pin  # GPIO23
RX: microcontroller.Pin  # GPIO17
IO17: microcontroller.Pin  # GPIO17
TX: microcontroller.Pin  # GPIO16
IO16: microcontroller.Pin  # GPIO16
BUTTON: microcontroller.Pin  # GPIO9
NEOPIXEL: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
LED: microcontroller.Pin  # GPIO15
IO15: microcontroller.Pin  # GPIO15
D13: microcontroller.Pin  # GPIO15
IO14: microcontroller.Pin  # GPIO14
D12: microcontroller.Pin  # GPIO14
IO0: microcontroller.Pin  # GPIO0
D11: microcontroller.Pin  # GPIO0
IO8: microcontroller.Pin  # GPIO8
D10: microcontroller.Pin  # GPIO8
IO7: microcontroller.Pin  # GPIO7
D9: microcontroller.Pin  # GPIO7
SCL: microcontroller.Pin  # GPIO18
IO18: microcontroller.Pin  # GPIO18
SDA: microcontroller.Pin  # GPIO19
IO19: microcontroller.Pin  # GPIO19
NEOPIXEL_I2C_POWER: microcontroller.Pin  # GPIO20


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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
