# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Metro ESP32S2
 - port: espressif
 - board_id: adafruit_metro_esp32s2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO17
IO17: microcontroller.Pin  # GPIO17
A1: microcontroller.Pin  # GPIO18
IO18: microcontroller.Pin  # GPIO18
A2: microcontroller.Pin  # GPIO1
IO1: microcontroller.Pin  # GPIO1
A3: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO2
A4: microcontroller.Pin  # GPIO3
IO3: microcontroller.Pin  # GPIO3
A5: microcontroller.Pin  # GPIO4
IO4: microcontroller.Pin  # GPIO4
RX: microcontroller.Pin  # GPIO5
IO5: microcontroller.Pin  # GPIO5
TX: microcontroller.Pin  # GPIO6
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
IO21: microcontroller.Pin  # GPIO21
SDA: microcontroller.Pin  # GPIO33
IO33: microcontroller.Pin  # GPIO33
SCL: microcontroller.Pin  # GPIO34
IO34: microcontroller.Pin  # GPIO34
SCK: microcontroller.Pin  # GPIO36
IO36: microcontroller.Pin  # GPIO36
MOSI: microcontroller.Pin  # GPIO35
IO35: microcontroller.Pin  # GPIO35
MISO: microcontroller.Pin  # GPIO37
IO37: microcontroller.Pin  # GPIO37
IO42: microcontroller.Pin  # GPIO42
LED: microcontroller.Pin  # GPIO42
NEOPIXEL: microcontroller.Pin  # GPIO45
IO45: microcontroller.Pin  # GPIO45
DEBUG_RX: microcontroller.Pin  # GPIO44
DEBUG_TX: microcontroller.Pin  # GPIO43


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
