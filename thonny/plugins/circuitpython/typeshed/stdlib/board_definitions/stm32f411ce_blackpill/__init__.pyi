# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for stm32f411ce-blackpill
 - port: stm
 - board_id: stm32f411ce_blackpill
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
B12: microcontroller.Pin  # PB12
B13: microcontroller.Pin  # PB13
B14: microcontroller.Pin  # PB14
B15: microcontroller.Pin  # PB15
A8: microcontroller.Pin  # PA08
A9: microcontroller.Pin  # PA09
A10: microcontroller.Pin  # PA10
A11: microcontroller.Pin  # PA11
A12: microcontroller.Pin  # PA12
A15: microcontroller.Pin  # PA15
B3: microcontroller.Pin  # PB03
B4: microcontroller.Pin  # PB04
B5: microcontroller.Pin  # PB05
B6: microcontroller.Pin  # PB06
B7: microcontroller.Pin  # PB07
B8: microcontroller.Pin  # PB08
B9: microcontroller.Pin  # PB09
B10: microcontroller.Pin  # PB10
B2: microcontroller.Pin  # PB02
B1: microcontroller.Pin  # PB01
B0: microcontroller.Pin  # PB00
A7: microcontroller.Pin  # PA07
A6: microcontroller.Pin  # PA06
A5: microcontroller.Pin  # PA05
A4: microcontroller.Pin  # PA04
A3: microcontroller.Pin  # PA03
A2: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA01
A0: microcontroller.Pin  # PA00
C15: microcontroller.Pin  # PC15
C14: microcontroller.Pin  # PC14
C13: microcontroller.Pin  # PC13
LED: microcontroller.Pin  # PC13
SDA: microcontroller.Pin  # PB07
SCL: microcontroller.Pin  # PB06


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
