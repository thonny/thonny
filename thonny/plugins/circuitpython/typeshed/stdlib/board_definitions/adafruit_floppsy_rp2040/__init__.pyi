# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Floppsy RP2040
 - port: raspberrypi
 - board_id: adafruit_floppsy_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
DENSITY: microcontroller.Pin  # GPIO0
SELECT: microcontroller.Pin  # GPIO1
MOTOR: microcontroller.Pin  # GPIO2
DIRECTION: microcontroller.Pin  # GPIO3
STEP: microcontroller.Pin  # GPIO4
WRDATA: microcontroller.Pin  # GPIO5
WRGATE: microcontroller.Pin  # GPIO6
SIDE: microcontroller.Pin  # GPIO7
FLOPPY_DIRECTION: microcontroller.Pin  # GPIO8
INDEX: microcontroller.Pin  # GPIO9
TRACK0: microcontroller.Pin  # GPIO10
WRPROT: microcontroller.Pin  # GPIO11
RDDATA: microcontroller.Pin  # GPIO12
READY: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO17
NEOPIXEL: microcontroller.Pin  # GPIO14
SD_CD: microcontroller.Pin  # GPIO24
SD_SCK: microcontroller.Pin  # GPIO18
SDIO_CLK: microcontroller.Pin  # GPIO18
SD_MOSI: microcontroller.Pin  # GPIO19
SDIO_COMMAND: microcontroller.Pin  # GPIO19
SD_MISO: microcontroller.Pin  # GPIO20
SDIO_DATA0: microcontroller.Pin  # GPIO20
SDIO_DATA1: microcontroller.Pin  # GPIO21
SDIO_DATA2: microcontroller.Pin  # GPIO22
SD_CS: microcontroller.Pin  # GPIO23
SDIO_DATA3: microcontroller.Pin  # GPIO23


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


# Unmapped:
#   none
