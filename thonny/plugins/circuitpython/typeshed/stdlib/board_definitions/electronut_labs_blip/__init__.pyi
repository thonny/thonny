# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Electronut Labs Blip
 - port: nordic
 - board_id: electronut_labs_blip
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # P0_03
A1: microcontroller.Pin  # P0_04
A2: microcontroller.Pin  # P0_28
A3: microcontroller.Pin  # P0_29
A4: microcontroller.Pin  # P0_30
A5: microcontroller.Pin  # P0_31
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
D2: microcontroller.Pin  # P0_02
D4: microcontroller.Pin  # P0_04
D6: microcontroller.Pin  # P0_06
D8: microcontroller.Pin  # P0_08
D19: microcontroller.Pin  # P0_19
D21: microcontroller.Pin  # P0_21
D26: microcontroller.Pin  # P0_26
D27: microcontroller.Pin  # P0_27
D29: microcontroller.Pin  # P0_29
D31: microcontroller.Pin  # P0_31
D33: microcontroller.Pin  # P1_01
D36: microcontroller.Pin  # P1_04
D38: microcontroller.Pin  # P1_06
D3: microcontroller.Pin  # P0_03
D5: microcontroller.Pin  # P0_05
D7: microcontroller.Pin  # P0_07
D16: microcontroller.Pin  # P0_16
D20: microcontroller.Pin  # P0_20
D22: microcontroller.Pin  # P0_22
D23: microcontroller.Pin  # P0_23
D28: microcontroller.Pin  # P0_28
D30: microcontroller.Pin  # P0_30
D32: microcontroller.Pin  # P1_00
D35: microcontroller.Pin  # P1_03
D37: microcontroller.Pin  # P1_05
D40: microcontroller.Pin  # P1_08
D11: microcontroller.Pin  # P0_11
D12: microcontroller.Pin  # P0_12
SCL: microcontroller.Pin  # P0_11
SDA: microcontroller.Pin  # P0_12
SCK: microcontroller.Pin  # P0_25
MOSI: microcontroller.Pin  # P0_24
MISO: microcontroller.Pin  # P1_02
CS: microcontroller.Pin  # P0_17
TX: microcontroller.Pin  # P0_06
RX: microcontroller.Pin  # P0_08
L: microcontroller.Pin  # P0_14
RED_LED: microcontroller.Pin  # P0_14
LED: microcontroller.Pin  # P0_14
BLUE_LED: microcontroller.Pin  # P0_15
GREEN_LED: microcontroller.Pin  # P0_13
BUTTON: microcontroller.Pin  # P1_07
RESET: microcontroller.Pin  # P0_18


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