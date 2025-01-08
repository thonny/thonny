# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PyboardV1_1
 - port: stm
 - board_id: pyboard_v11
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rtc, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
Y1: microcontroller.Pin  # PC06
Y2: microcontroller.Pin  # PC07
Y3: microcontroller.Pin  # PB08
Y4: microcontroller.Pin  # PB09
Y5: microcontroller.Pin  # PB12
Y6: microcontroller.Pin  # PB13
Y7: microcontroller.Pin  # PB14
Y8: microcontroller.Pin  # PB15
Y9: microcontroller.Pin  # PB10
Y10: microcontroller.Pin  # PB11
Y11: microcontroller.Pin  # PB00
Y12: microcontroller.Pin  # PB01
X1: microcontroller.Pin  # PA00
X2: microcontroller.Pin  # PA01
X3: microcontroller.Pin  # PA02
X4: microcontroller.Pin  # PA03
X5: microcontroller.Pin  # PA04
X6: microcontroller.Pin  # PA05
X7: microcontroller.Pin  # PA06
X8: microcontroller.Pin  # PA07
X9: microcontroller.Pin  # PB06
X10: microcontroller.Pin  # PB07
X11: microcontroller.Pin  # PC04
X12: microcontroller.Pin  # PC05
X17: microcontroller.Pin  # PB03
X18: microcontroller.Pin  # PC13
X19: microcontroller.Pin  # PC00
X20: microcontroller.Pin  # PC01
X21: microcontroller.Pin  # PC02
X22: microcontroller.Pin  # PC03
P2: microcontroller.Pin  # PB04
P3: microcontroller.Pin  # PA15
P4: microcontroller.Pin  # PA14
P5: microcontroller.Pin  # PA13
LED1: microcontroller.Pin  # PB04
LED2: microcontroller.Pin  # PA15
LED3: microcontroller.Pin  # PA14
LED4: microcontroller.Pin  # PA13
SCL: microcontroller.Pin  # PB06
SDA: microcontroller.Pin  # PB07


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
