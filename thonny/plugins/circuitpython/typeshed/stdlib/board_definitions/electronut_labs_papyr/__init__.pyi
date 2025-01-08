# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Electronut Labs Papyr
 - port: nordic
 - board_id: electronut_labs_papyr
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A5: microcontroller.Pin  # P0_05
A6: microcontroller.Pin  # P0_06
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
D5: microcontroller.Pin  # P0_05
D6: microcontroller.Pin  # P0_06
D7: microcontroller.Pin  # P0_07
D8: microcontroller.Pin  # P0_08
D13: microcontroller.Pin  # P0_13
D14: microcontroller.Pin  # P0_14
D15: microcontroller.Pin  # P0_15
SCK: microcontroller.Pin  # P0_31
MOSI: microcontroller.Pin  # P0_29
MISO: microcontroller.Pin  # P1_01
CS: microcontroller.Pin  # P0_30
BUSY: microcontroller.Pin  # P0_03
DC: microcontroller.Pin  # P0_28
RES: microcontroller.Pin  # P0_02
EINK_EN: microcontroller.Pin  # P0_11
TX: microcontroller.Pin  # P0_08
RX: microcontroller.Pin  # P0_07
SCL: microcontroller.Pin  # P0_06
SDA: microcontroller.Pin  # P0_05
L: microcontroller.Pin  # P0_14
LED: microcontroller.Pin  # P0_14
RED_LED: microcontroller.Pin  # P0_14
BLUE_LED: microcontroller.Pin  # P0_15
GREEN_LED: microcontroller.Pin  # P0_13


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
