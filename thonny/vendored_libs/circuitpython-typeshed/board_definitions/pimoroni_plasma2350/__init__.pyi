# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Plasma 2350
 - port: raspberrypi
 - board_id: pimoroni_plasma2350
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
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
SW_A: microcontroller.Pin  # GPIO12
BUTTON: microcontroller.Pin  # GPIO12
SW_BOOT: microcontroller.Pin  # GPIO22
BOOT: microcontroller.Pin  # GPIO22
USER_SW: microcontroller.Pin  # GPIO22
CLK: microcontroller.Pin  # GPIO14
GP14: microcontroller.Pin  # GPIO14
DATA: microcontroller.Pin  # GPIO15
GP15: microcontroller.Pin  # GPIO15
LED_R: microcontroller.Pin  # GPIO16
LED_G: microcontroller.Pin  # GPIO17
LED_B: microcontroller.Pin  # GPIO18
INT: microcontroller.Pin  # GPIO19
GP19: microcontroller.Pin  # GPIO19
SDA: microcontroller.Pin  # GPIO20
GP20: microcontroller.Pin  # GPIO20
SCL: microcontroller.Pin  # GPIO21
GP21: microcontroller.Pin  # GPIO21
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
SPICE_CS: microcontroller.Pin  # GPIO9
SPICE_SCK: microcontroller.Pin  # GPIO10
SCK: microcontroller.Pin  # GPIO10
SPICE_TX: microcontroller.Pin  # GPIO11
MOSI: microcontroller.Pin  # GPIO11
SPICE_RX: microcontroller.Pin  # GPIO8
MISO: microcontroller.Pin  # GPIO8
SPICE_BL: microcontroller.Pin  # GPIO7
TFT_BACKLIGHT: microcontroller.Pin  # GPIO7


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
