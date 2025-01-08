# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather MIMXRT1011
 - port: mimxrt10xx
 - board_id: feather_m7_1011
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_esp32spi, adafruit_requests
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO_AD_11
A1: microcontroller.Pin  # GPIO_AD_10
A2: microcontroller.Pin  # GPIO_AD_09
A3: microcontroller.Pin  # GPIO_AD_08
A4: microcontroller.Pin  # GPIO_AD_07
A5: microcontroller.Pin  # GPIO_AD_05
D5: microcontroller.Pin  # GPIO_10
D6: microcontroller.Pin  # GPIO_09
D9: microcontroller.Pin  # GPIO_08
D10: microcontroller.Pin  # GPIO_07
D11: microcontroller.Pin  # GPIO_06
D12: microcontroller.Pin  # GPIO_05
LED: microcontroller.Pin  # GPIO_04
D13: microcontroller.Pin  # GPIO_04
D14: microcontroller.Pin  # GPIO_AD_00
SCK: microcontroller.Pin  # GPIO_AD_06
MISO: microcontroller.Pin  # GPIO_AD_03
MOSI: microcontroller.Pin  # GPIO_AD_04
TX: microcontroller.Pin  # GPIO_AD_02
RX: microcontroller.Pin  # GPIO_AD_01
SDA: microcontroller.Pin  # GPIO_11
SCL: microcontroller.Pin  # GPIO_12
NEOPIXEL: microcontroller.Pin  # GPIO_00


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
