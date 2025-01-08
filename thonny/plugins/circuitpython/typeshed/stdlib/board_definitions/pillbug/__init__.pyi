# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PillBug
 - port: nordic
 - board_id: pillbug
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
P0_02: microcontroller.Pin  # P0_02
P0_04: microcontroller.Pin  # P0_04
P0_06: microcontroller.Pin  # P0_06
P0_08: microcontroller.Pin  # P0_08
P0_09: microcontroller.Pin  # P0_09
P0_10: microcontroller.Pin  # P0_10
P0_11: microcontroller.Pin  # P0_11
P0_12: microcontroller.Pin  # P0_12
P0_13: microcontroller.Pin  # P0_13
P0_15: microcontroller.Pin  # P0_15
P0_17: microcontroller.Pin  # P0_17
P0_20: microcontroller.Pin  # P0_20
P0_22: microcontroller.Pin  # P0_22
P0_24: microcontroller.Pin  # P0_24
P0_26: microcontroller.Pin  # P0_26
P0_29: microcontroller.Pin  # P0_29
P0_31: microcontroller.Pin  # P0_31
P1_00: microcontroller.Pin  # P1_00
P1_01: microcontroller.Pin  # P1_01
P1_02: microcontroller.Pin  # P1_02
P1_04: microcontroller.Pin  # P1_04
P1_06: microcontroller.Pin  # P1_06
P1_07: microcontroller.Pin  # P1_07
P1_11: microcontroller.Pin  # P1_11
P1_13: microcontroller.Pin  # P1_13
P1_15: microcontroller.Pin  # P1_15
AIN0: microcontroller.Pin  # P0_02
AIN2: microcontroller.Pin  # P0_03
AIN5: microcontroller.Pin  # P0_29
AIN7: microcontroller.Pin  # P0_31
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
VOLTAGE_MONITOR: microcontroller.Pin  # P0_04
BATTERY: microcontroller.Pin  # P0_04
VCC_OFF: microcontroller.Pin  # P1_07
LED: microcontroller.Pin  # P0_20
RX: microcontroller.Pin  # P0_08
TX: microcontroller.Pin  # P0_06
SCL: microcontroller.Pin  # P0_13
SDA: microcontroller.Pin  # P0_15
SCK: microcontroller.Pin  # P1_13
MOSI: microcontroller.Pin  # P0_10
MISO: microcontroller.Pin  # P1_11


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
