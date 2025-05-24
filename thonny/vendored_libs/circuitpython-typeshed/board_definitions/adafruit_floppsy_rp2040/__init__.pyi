# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Floppsy RP2040
 - port: raspberrypi
 - board_id: adafruit_floppsy_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
PERIPH_RESET: microcontroller.Pin  # GPIO0
DENSITY: microcontroller.Pin  # GPIO1
SELECT: microcontroller.Pin  # GPIO2
MOTOR: microcontroller.Pin  # GPIO3
DIRECTION: microcontroller.Pin  # GPIO4
STEP: microcontroller.Pin  # GPIO5
WRDATA: microcontroller.Pin  # GPIO6
WRGATE: microcontroller.Pin  # GPIO7
SIDE: microcontroller.Pin  # GPIO8
FLOPPY_DIRECTION: microcontroller.Pin  # GPIO9
INDEX: microcontroller.Pin  # GPIO10
TRACK0: microcontroller.Pin  # GPIO11
WRPROT: microcontroller.Pin  # GPIO12
RDDATA: microcontroller.Pin  # GPIO13
READY: microcontroller.Pin  # GPIO14
FLOPPY_ENABLE: microcontroller.Pin  # GPIO15
SDA: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO17
NEOPIXEL: microcontroller.Pin  # GPIO22
SCK: microcontroller.Pin  # GPIO18
MISO: microcontroller.Pin  # GPIO19
MOSI: microcontroller.Pin  # GPIO20
SD_CS: microcontroller.Pin  # GPIO21
D0: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
D1: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27


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
#     { MP_OBJ_NEW_QSTR(MP_QSTR_TFT_DC), MP_ROM_PTR(CIRCUITPY_BOARD_TFT_DC) },
#     { MP_OBJ_NEW_QSTR(MP_QSTR_TFT_CS), MP_ROM_PTR(CIRCUITPY_BOARD_TFT_CS) },
#     { MP_OBJ_NEW_QSTR(MP_QSTR_TFT_BACKLIGHT), MP_ROM_PTR(CIRCUITPY_BOARD_TFT_BACKLIGHT) },
#     { MP_ROM_QSTR(MP_QSTR_DISPLAY), MP_ROM_PTR(&displays[0].framebuffer_display)},
