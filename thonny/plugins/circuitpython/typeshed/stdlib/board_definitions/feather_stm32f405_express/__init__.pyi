# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather STM32F405 Express
 - port: stm
 - board_id: feather_stm32f405_express
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rtc, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA04
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA06
A3: microcontroller.Pin  # PA07
A4: microcontroller.Pin  # PC04
A5: microcontroller.Pin  # PC05
VOLTAGE_MONITOR: microcontroller.Pin  # PA03
D5: microcontroller.Pin  # PC07
D6: microcontroller.Pin  # PC06
D9: microcontroller.Pin  # PB08
D10: microcontroller.Pin  # PB09
D11: microcontroller.Pin  # PC03
D12: microcontroller.Pin  # PC02
LED: microcontroller.Pin  # PC01
D13: microcontroller.Pin  # PC01
SDA: microcontroller.Pin  # PB07
SCL: microcontroller.Pin  # PB06
SCK: microcontroller.Pin  # PB13
MISO: microcontroller.Pin  # PB14
MOSI: microcontroller.Pin  # PB15
TX: microcontroller.Pin  # PB10
RX: microcontroller.Pin  # PB11
NEOPIXEL: microcontroller.Pin  # PC00
SDIO_CLOCK: microcontroller.Pin  # PC12
SDIO_COMMAND: microcontroller.Pin  # PD02
CAN_RX: microcontroller.Pin  # PB08
CAN_TX: microcontroller.Pin  # PB09


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

SDIO_DATA: Tuple[Any]


# Unmapped:
#   none
