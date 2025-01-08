# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Metro MIMXRT1011
 - port: mimxrt10xx
 - board_id: adafruit_metro_m7_1011_sd
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
A0: microcontroller.Pin  # GPIO_AD_02
A1: microcontroller.Pin  # GPIO_AD_01
A2: microcontroller.Pin  # GPIO_AD_00
A3: microcontroller.Pin  # GPIO_AD_05
A4: microcontroller.Pin  # GPIO_AD_10
A5: microcontroller.Pin  # GPIO_AD_08
D0: microcontroller.Pin  # GPIO_09
RX: microcontroller.Pin  # GPIO_09
D1: microcontroller.Pin  # GPIO_10
TX: microcontroller.Pin  # GPIO_10
D2: microcontroller.Pin  # GPIO_13
D3: microcontroller.Pin  # GPIO_12
D4: microcontroller.Pin  # GPIO_SD_00
D5: microcontroller.Pin  # GPIO_SD_01
D6: microcontroller.Pin  # GPIO_SD_02
D7: microcontroller.Pin  # GPIO_11
D8: microcontroller.Pin  # GPIO_08
D9: microcontroller.Pin  # GPIO_07
D10: microcontroller.Pin  # GPIO_06
D11: microcontroller.Pin  # GPIO_05
D12: microcontroller.Pin  # GPIO_04
LED: microcontroller.Pin  # GPIO_03
D13: microcontroller.Pin  # GPIO_03
SD_CD: microcontroller.Pin  # GPIO_AD_11
SD_CS: microcontroller.Pin  # GPIO_AD_14
SCK: microcontroller.Pin  # GPIO_AD_06
MISO: microcontroller.Pin  # GPIO_AD_03
MOSI: microcontroller.Pin  # GPIO_AD_04
SDA: microcontroller.Pin  # GPIO_01
SCL: microcontroller.Pin  # GPIO_02
NEOPIXEL: microcontroller.Pin  # GPIO_00
I2S_WORD_SELECT: microcontroller.Pin  # GPIO_06
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO_07
I2S_DATA: microcontroller.Pin  # GPIO_04


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
