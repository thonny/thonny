# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for BastBLE
 - port: nordic
 - board_id: bastble
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
D2: microcontroller.Pin  # P1_11
D3: microcontroller.Pin  # P1_10
D4: microcontroller.Pin  # P1_00
D5: microcontroller.Pin  # P1_02
D6: microcontroller.Pin  # P1_13
D7: microcontroller.Pin  # P1_06
D8: microcontroller.Pin  # P0_15
D9: microcontroller.Pin  # P0_06
D10: microcontroller.Pin  # P1_09
D11: microcontroller.Pin  # P0_08
D12: microcontroller.Pin  # P0_26
D13: microcontroller.Pin  # P0_07
A0: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_28
A2: microcontroller.Pin  # P0_05
A3: microcontroller.Pin  # P0_03
A4: microcontroller.Pin  # P0_30
SDA: microcontroller.Pin  # P1_11
A5: microcontroller.Pin  # P0_29
SCL: microcontroller.Pin  # P1_10
MOSI: microcontroller.Pin  # P1_06
MISO: microcontroller.Pin  # P0_15
SCK: microcontroller.Pin  # P1_00
LED: microcontroller.Pin  # P0_24
AREF: microcontroller.Pin  # P0_31
VBAT: microcontroller.Pin  # P0_26
TX: microcontroller.Pin  # P0_10
RX: microcontroller.Pin  # P0_09


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
