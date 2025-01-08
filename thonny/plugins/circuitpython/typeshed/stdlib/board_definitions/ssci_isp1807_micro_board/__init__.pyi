# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SSCI ISP1807 Micro Board
 - port: nordic
 - board_id: ssci_isp1807_micro_board
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
D0: microcontroller.Pin  # P0_19
D1: microcontroller.Pin  # P0_30
D2: microcontroller.Pin  # P0_29
D3: microcontroller.Pin  # P0_23
D4: microcontroller.Pin  # P0_28
A4: microcontroller.Pin  # P0_28
D5: microcontroller.Pin  # P0_09
D6: microcontroller.Pin  # P0_12
D7: microcontroller.Pin  # P0_10
D8: microcontroller.Pin  # P0_14
D9: microcontroller.Pin  # P0_26
D10: microcontroller.Pin  # P0_17
D14: microcontroller.Pin  # P0_08
D15: microcontroller.Pin  # P0_06
D16: microcontroller.Pin  # P0_13
D17: microcontroller.Pin  # P0_31
D18: microcontroller.Pin  # P0_02
D19: microcontroller.Pin  # P0_03
D20: microcontroller.Pin  # P0_04
D21: microcontroller.Pin  # P0_05
A0: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_03
A2: microcontroller.Pin  # P0_04
A3: microcontroller.Pin  # P0_05
A5: microcontroller.Pin  # P0_29
A6: microcontroller.Pin  # P0_30
LED: microcontroller.Pin  # P0_31
SDA: microcontroller.Pin  # P0_29
SCL: microcontroller.Pin  # P0_23
MOSI: microcontroller.Pin  # P0_13
MISO: microcontroller.Pin  # P0_08
SCK: microcontroller.Pin  # P0_06
TX: microcontroller.Pin  # P0_30
RX: microcontroller.Pin  # P0_19


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
