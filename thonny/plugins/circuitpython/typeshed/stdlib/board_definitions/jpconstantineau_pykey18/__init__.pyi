# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PyKey 18 Numpad
 - port: raspberrypi
 - board_id: jpconstantineau_pykey18
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
COL1: microcontroller.Pin  # GPIO0
COL2: microcontroller.Pin  # GPIO1
COL3: microcontroller.Pin  # GPIO2
COL4: microcontroller.Pin  # GPIO3
ROW1: microcontroller.Pin  # GPIO14
ROW2: microcontroller.Pin  # GPIO15
ROW3: microcontroller.Pin  # GPIO16
ROW4: microcontroller.Pin  # GPIO17
ROW5: microcontroller.Pin  # GPIO18
SPEAKER: microcontroller.Pin  # GPIO21
LED: microcontroller.Pin  # GPIO24
ENCA: microcontroller.Pin  # GPIO27
ENCB: microcontroller.Pin  # GPIO28
NEOPIXEL: microcontroller.Pin  # GPIO29
SDA: microcontroller.Pin  # GPIO22
SCL: microcontroller.Pin  # GPIO23


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
