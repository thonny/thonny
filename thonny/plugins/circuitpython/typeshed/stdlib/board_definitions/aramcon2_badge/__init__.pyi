# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ARAMCON2 Badge
 - port: nordic
 - board_id: aramcon2_badge
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
UP_BUTTON: microcontroller.Pin  # P0_31
LEFT_BUTTON: microcontroller.Pin  # P0_29
DOWN_BUTTON: microcontroller.Pin  # P1_13
RIGHT_BUTTON: microcontroller.Pin  # P0_02
ACTION_BUTTON: microcontroller.Pin  # P0_10
LED: microcontroller.Pin  # P1_11
SCL: microcontroller.Pin  # P0_28
SDA: microcontroller.Pin  # P0_03
SCK: microcontroller.Pin  # P0_01
MOSI: microcontroller.Pin  # P1_10
MISO: microcontroller.Pin  # P1_09
GPIO1: microcontroller.Pin  # P0_04
GPIO2: microcontroller.Pin  # P0_05
D1: microcontroller.Pin  # P0_15
D2: microcontroller.Pin  # P0_00
D3: microcontroller.Pin  # P0_13
D4: microcontroller.Pin  # P0_24
DISP_BUSY: microcontroller.Pin  # P0_26
DISP_CS: microcontroller.Pin  # P0_07
DISP_DC: microcontroller.Pin  # P0_12
DISP_RESET: microcontroller.Pin  # P0_06
NEOPIXEL: microcontroller.Pin  # P0_08
VIBRATION_MOTOR: microcontroller.Pin  # P0_17
BATTERY_SENSE: microcontroller.Pin  # P0_30


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
