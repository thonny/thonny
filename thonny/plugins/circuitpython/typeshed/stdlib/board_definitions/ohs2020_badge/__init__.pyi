# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Open Hardware Summit 2020 Badge
 - port: nordic
 - board_id: ohs2020_badge
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
MICROPHONE_CLOCK: microcontroller.Pin  # P0_25
MICROPHONE_DATA: microcontroller.Pin  # P0_28
TFT_RESET: microcontroller.Pin  # P0_13
TFT_BACKLIGHT: microcontroller.Pin  # P0_02
TFT_CS: microcontroller.Pin  # P0_14
TFT_DC: microcontroller.Pin  # P0_08
TFT_SCK: microcontroller.Pin  # P0_11
TFT_MOSI: microcontroller.Pin  # P0_12
SCL: microcontroller.Pin  # P1_14
SDA: microcontroller.Pin  # P1_15
BUTTON_SW1: microcontroller.Pin  # P0_29
BUTTON_SW2: microcontroller.Pin  # P0_03
BUTTON_SW3: microcontroller.Pin  # P0_17
BUTTON_SW4: microcontroller.Pin  # P1_03


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
