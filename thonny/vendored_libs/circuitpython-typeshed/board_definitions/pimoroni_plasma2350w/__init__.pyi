# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Plasma 2350W
 - port: raspberrypi
 - board_id: pimoroni_plasma2350w
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, cyw43, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
GP1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
GP12: microcontroller.Pin  # GPIO12
SW_A: microcontroller.Pin  # GPIO12
BUTTON: microcontroller.Pin  # GPIO12
GP14: microcontroller.Pin  # GPIO14
CLK: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
DATA: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
LED_R: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
LED_G: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
LED_B: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
INT: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
SDA: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
SCL: microcontroller.Pin  # GPIO21
GP22: microcontroller.Pin  # GPIO22
SW_BOOT: microcontroller.Pin  # GPIO22
BOOT: microcontroller.Pin  # GPIO22
USER_SW: microcontroller.Pin  # GPIO22
GP26: microcontroller.Pin  # GPIO26
GP26_A0: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27: microcontroller.Pin  # GPIO27
GP27_A1: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28: microcontroller.Pin  # GPIO28
GP28_A2: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28


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

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
