# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Feather MIMXRT1062
 - port: mimxrt10xx
 - board_id: feather_mimxrt1062
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO_AD_B0_13
A1: microcontroller.Pin  # GPIO_AD_B1_10
A2: microcontroller.Pin  # GPIO_AD_B0_12
A3: microcontroller.Pin  # GPIO_AD_B1_15
A4: microcontroller.Pin  # GPIO_AD_B1_11
A5: microcontroller.Pin  # GPIO_AD_B0_14
D5: microcontroller.Pin  # GPIO_EMC_15
D6: microcontroller.Pin  # GPIO_EMC_28
D9: microcontroller.Pin  # GPIO_EMC_29
D10: microcontroller.Pin  # GPIO_EMC_04
D11: microcontroller.Pin  # GPIO_EMC_10
D12: microcontroller.Pin  # GPIO_EMC_23
LED: microcontroller.Pin  # GPIO_EMC_12
D13: microcontroller.Pin  # GPIO_EMC_12
D14: microcontroller.Pin  # GPIO_B1_08
SCK: microcontroller.Pin  # GPIO_B1_07
MISO: microcontroller.Pin  # GPIO_B1_05
MOSI: microcontroller.Pin  # GPIO_B1_06
TX: microcontroller.Pin  # GPIO_B1_02
RX: microcontroller.Pin  # GPIO_B1_03
SDA: microcontroller.Pin  # GPIO_EMC_21
SCL: microcontroller.Pin  # GPIO_EMC_22
NEOPIXEL: microcontroller.Pin  # GPIO_SD_B1_01


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
