# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for BBQ20KBD
 - port: raspberrypi
 - board_id: solderparty_bbq20kbd
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_hid
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
INT: microcontroller.Pin  # GPIO0
PERIPHERAL_SDA: microcontroller.Pin  # GPIO28
PERIPHERAL_SCL: microcontroller.Pin  # GPIO29
ROW1: microcontroller.Pin  # GPIO1
ROW2: microcontroller.Pin  # GPIO2
ROW3: microcontroller.Pin  # GPIO3
ROW4: microcontroller.Pin  # GPIO4
ROW5: microcontroller.Pin  # GPIO5
ROW6: microcontroller.Pin  # GPIO6
ROW7: microcontroller.Pin  # GPIO7
COL1: microcontroller.Pin  # GPIO8
COL2: microcontroller.Pin  # GPIO9
COL3: microcontroller.Pin  # GPIO14
COL4: microcontroller.Pin  # GPIO13
COL5: microcontroller.Pin  # GPIO12
COL6: microcontroller.Pin  # GPIO11
BTN1: microcontroller.Pin  # GPIO10
BACKLIGHT: microcontroller.Pin  # GPIO25
TP_RESET: microcontroller.Pin  # GPIO16
TP_MOTION: microcontroller.Pin  # GPIO22
TP_SHUTDOWN: microcontroller.Pin  # GPIO24
SCL: microcontroller.Pin  # GPIO23
SDA: microcontroller.Pin  # GPIO18
TX: microcontroller.Pin  # GPIO20


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
