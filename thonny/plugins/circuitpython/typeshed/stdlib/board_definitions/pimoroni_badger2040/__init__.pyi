# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Badger 2040
 - port: raspberrypi
 - board_id: pimoroni_badger2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
INT: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO5
SW_DOWN: microcontroller.Pin  # GPIO11
SW_A: microcontroller.Pin  # GPIO12
SW_B: microcontroller.Pin  # GPIO13
SW_C: microcontroller.Pin  # GPIO14
SW_UP: microcontroller.Pin  # GPIO15
MISO: microcontroller.Pin  # GPIO16
INKY_CS: microcontroller.Pin  # GPIO17
SCK: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO19
INKY_DC: microcontroller.Pin  # GPIO20
INKY_RST: microcontroller.Pin  # GPIO21
USER_SW: microcontroller.Pin  # GPIO23
VBUS_DETECT: microcontroller.Pin  # GPIO24
USER_LED: microcontroller.Pin  # GPIO25
INKY_BUSY: microcontroller.Pin  # GPIO26
VREF_POWER: microcontroller.Pin  # GPIO27
REF_1V2: microcontroller.Pin  # GPIO28
VBAT_SENSE: microcontroller.Pin  # GPIO29


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

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
