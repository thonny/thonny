# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for IkigaiSense Vita nRF52840
 - port: nordic
 - board_id: ikigaisense_vita
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
A0: microcontroller.Pin  # P0_29
A1: microcontroller.Pin  # P1_15
A2: microcontroller.Pin  # P1_13
D0: microcontroller.Pin  # P0_24
D1: microcontroller.Pin  # P0_22
D2: microcontroller.Pin  # P0_20
D5: microcontroller.Pin  # P0_17
D7: microcontroller.Pin  # P0_15
D9: microcontroller.Pin  # P0_13
RX: microcontroller.Pin  # P0_24
TX: microcontroller.Pin  # P0_22
SCL: microcontroller.Pin  # P0_08
SDA: microcontroller.Pin  # P0_04
MAXTEMP_SCL: microcontroller.Pin  # P0_31
MAXTEMP_SDA: microcontroller.Pin  # P0_30
ACC_SCL: microcontroller.Pin  # P1_11
ACC_SDA: microcontroller.Pin  # P1_10
ADDON_SCL: microcontroller.Pin  # P1_09
ADDON_SDA: microcontroller.Pin  # P0_06
L: microcontroller.Pin  # P0_27
LED: microcontroller.Pin  # P0_27
YELLOW_LED: microcontroller.Pin  # P0_27


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
