# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for iMX RT1011 Nano Kit
 - port: mimxrt10xx
 - board_id: makerdiary_imxrt1011_nanokit
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: adafruit_hid, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO_AD_00
A1: microcontroller.Pin  # GPIO_AD_01
A2: microcontroller.Pin  # GPIO_AD_02
A3: microcontroller.Pin  # GPIO_AD_03
A4: microcontroller.Pin  # GPIO_AD_04
A5: microcontroller.Pin  # GPIO_AD_05
A6: microcontroller.Pin  # GPIO_AD_06
A7: microcontroller.Pin  # GPIO_AD_07
A8: microcontroller.Pin  # GPIO_AD_08
A9: microcontroller.Pin  # GPIO_AD_09
A10: microcontroller.Pin  # GPIO_AD_10
A11: microcontroller.Pin  # GPIO_AD_11
A14: microcontroller.Pin  # GPIO_AD_14
D0: microcontroller.Pin  # GPIO_00
D1: microcontroller.Pin  # GPIO_01
D2: microcontroller.Pin  # GPIO_02
D3: microcontroller.Pin  # GPIO_03
D4: microcontroller.Pin  # GPIO_04
D5: microcontroller.Pin  # GPIO_05
D6: microcontroller.Pin  # GPIO_06
D7: microcontroller.Pin  # GPIO_07
D8: microcontroller.Pin  # GPIO_08
D9: microcontroller.Pin  # GPIO_09
D10: microcontroller.Pin  # GPIO_10
D11: microcontroller.Pin  # GPIO_11
D12: microcontroller.Pin  # GPIO_12
D13: microcontroller.Pin  # GPIO_13
SD0: microcontroller.Pin  # GPIO_SD_00
SD1: microcontroller.Pin  # GPIO_SD_01
SD2: microcontroller.Pin  # GPIO_SD_02
SD3: microcontroller.Pin  # GPIO_SD_03
SD4: microcontroller.Pin  # GPIO_SD_04
SD5: microcontroller.Pin  # GPIO_SD_05
SD13: microcontroller.Pin  # GPIO_SD_13
LED: microcontroller.Pin  # GPIO_SD_04
USR_BTN: microcontroller.Pin  # GPIO_SD_03
DCDC_MODE: microcontroller.Pin  # GPIO_SD_13
SCK: microcontroller.Pin  # GPIO_AD_06
MISO: microcontroller.Pin  # GPIO_AD_03
MOSI: microcontroller.Pin  # GPIO_AD_04
SDA: microcontroller.Pin  # GPIO_01
SCL: microcontroller.Pin  # GPIO_02
NEOPIXEL: microcontroller.Pin  # GPIO_00
I2S_WORD_SELECT: microcontroller.Pin  # GPIO_06
I2S_WSEL: microcontroller.Pin  # GPIO_06
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO_07
I2S_BCLK: microcontroller.Pin  # GPIO_07
I2S_DATA: microcontroller.Pin  # GPIO_04
I2S_DOUT: microcontroller.Pin  # GPIO_04


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
