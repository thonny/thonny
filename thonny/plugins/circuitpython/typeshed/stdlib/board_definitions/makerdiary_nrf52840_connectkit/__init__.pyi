# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Makerdiary nRF52840 Connect Kit
 - port: nordic
 - board_id: makerdiary_nrf52840_connectkit
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_ble, adafruit_hid, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
P3: microcontroller.Pin  # P0_03
P4: microcontroller.Pin  # P0_04
P5: microcontroller.Pin  # P0_05
P6: microcontroller.Pin  # P0_06
P7: microcontroller.Pin  # P0_07
P8: microcontroller.Pin  # P0_08
P9: microcontroller.Pin  # P0_09
P10: microcontroller.Pin  # P0_10
P11: microcontroller.Pin  # P0_11
P12: microcontroller.Pin  # P0_12
P13: microcontroller.Pin  # P0_13
P14: microcontroller.Pin  # P0_14
P15: microcontroller.Pin  # P0_15
P16: microcontroller.Pin  # P0_16
P18: microcontroller.Pin  # P0_18
P24: microcontroller.Pin  # P0_24
P25: microcontroller.Pin  # P0_25
P26: microcontroller.Pin  # P0_26
P27: microcontroller.Pin  # P0_27
P28: microcontroller.Pin  # P0_28
P29: microcontroller.Pin  # P0_29
P30: microcontroller.Pin  # P0_30
P31: microcontroller.Pin  # P0_31
P32: microcontroller.Pin  # P1_00
P33: microcontroller.Pin  # P1_01
P34: microcontroller.Pin  # P1_02
P35: microcontroller.Pin  # P1_03
P36: microcontroller.Pin  # P1_04
P37: microcontroller.Pin  # P1_05
P38: microcontroller.Pin  # P1_06
P39: microcontroller.Pin  # P1_07
P40: microcontroller.Pin  # P1_08
P41: microcontroller.Pin  # P1_09
P42: microcontroller.Pin  # P1_10
P43: microcontroller.Pin  # P1_11
P44: microcontroller.Pin  # P1_12
P45: microcontroller.Pin  # P1_13
P46: microcontroller.Pin  # P1_14
P47: microcontroller.Pin  # P1_15
A0: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_03
A2: microcontroller.Pin  # P0_04
A3: microcontroller.Pin  # P0_05
A4: microcontroller.Pin  # P0_28
A5: microcontroller.Pin  # P0_29
A6: microcontroller.Pin  # P0_30
A7: microcontroller.Pin  # P0_31
MEAS_EN: microcontroller.Pin  # P1_14
MODE: microcontroller.Pin  # P1_13
USER: microcontroller.Pin  # P1_00
RESET: microcontroller.Pin  # P0_18
LED0: microcontroller.Pin  # P1_15
LED1: microcontroller.Pin  # P1_10
LED2: microcontroller.Pin  # P1_11
LED3: microcontroller.Pin  # P1_12
RED_LED: microcontroller.Pin  # P1_10
GREEN_LED: microcontroller.Pin  # P1_11
BLUE_LED: microcontroller.Pin  # P1_12
TX: microcontroller.Pin  # P0_13
RX: microcontroller.Pin  # P0_12
SCL: microcontroller.Pin  # P0_24
SDA: microcontroller.Pin  # P0_25
SCK: microcontroller.Pin  # P0_14
MOSI: microcontroller.Pin  # P0_15
MISO: microcontroller.Pin  # P0_16


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
