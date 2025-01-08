# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun Thing Plus - RP2040
 - port: raspberrypi
 - board_id: sparkfun_thing_plus_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D6: microcontroller.Pin  # GPIO6
SDA: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
D23: microcontroller.Pin  # GPIO7
SCL: microcontroller.Pin  # GPIO7
D22: microcontroller.Pin  # GPIO22
D21: microcontroller.Pin  # GPIO21
D20: microcontroller.Pin  # GPIO20
D19: microcontroller.Pin  # GPIO19
D18: microcontroller.Pin  # GPIO18
D17: microcontroller.Pin  # GPIO17
D16: microcontroller.Pin  # GPIO16
NEOPIXEL: microcontroller.Pin  # GPIO8
D0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
D4: microcontroller.Pin  # GPIO4
MISO: microcontroller.Pin  # GPIO4
D3: microcontroller.Pin  # GPIO3
MOSI: microcontroller.Pin  # GPIO3
D2: microcontroller.Pin  # GPIO2
SCK: microcontroller.Pin  # GPIO2
A3: microcontroller.Pin  # GPIO29
D29: microcontroller.Pin  # GPIO29
A2: microcontroller.Pin  # GPIO28
D28: microcontroller.Pin  # GPIO28
A1: microcontroller.Pin  # GPIO27
D27: microcontroller.Pin  # GPIO27
A0: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
SD_SCK: microcontroller.Pin  # GPIO14
SD_MOSI: microcontroller.Pin  # GPIO15
SD_MISO: microcontroller.Pin  # GPIO12
SD_CS: microcontroller.Pin  # GPIO9
LED: microcontroller.Pin  # GPIO25


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
