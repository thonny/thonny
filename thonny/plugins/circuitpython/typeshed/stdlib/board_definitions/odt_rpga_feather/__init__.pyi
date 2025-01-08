# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Oak Dev Tech RPGA Feather
 - port: raspberrypi
 - board_id: odt_rpga_feather
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
D27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
D28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
A29: microcontroller.Pin  # GPIO29
D3: microcontroller.Pin  # GPIO29
SCK: microcontroller.Pin  # GPIO2
MOSI: microcontroller.Pin  # GPIO3
MISO: microcontroller.Pin  # GPIO0
CS: microcontroller.Pin  # GPIO1
STEMMA_SDA: microcontroller.Pin  # GPIO8
TX: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
STEMMA_SCL: microcontroller.Pin  # GPIO9
RX: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
SDA: microcontroller.Pin  # GPIO10
D10: microcontroller.Pin  # GPIO10
F45: microcontroller.Pin  # GPIO10
SCL: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
F46: microcontroller.Pin  # GPIO11
D6: microcontroller.Pin  # GPIO6
F47: microcontroller.Pin  # GPIO6
D20: microcontroller.Pin  # GPIO20
F48: microcontroller.Pin  # GPIO20
F2: microcontroller.Pin  # GPIO16
F3: microcontroller.Pin  # GPIO17
F4: microcontroller.Pin  # GPIO18
F6: microcontroller.Pin  # GPIO19
CDONE: microcontroller.Pin  # GPIO5
F_RST: microcontroller.Pin  # GPIO4
F_SCK: microcontroller.Pin  # GPIO14
F_MOSI: microcontroller.Pin  # GPIO15
F_MISO: microcontroller.Pin  # GPIO12
F_CSN: microcontroller.Pin  # GPIO13
D21: microcontroller.Pin  # GPIO21
D22: microcontroller.Pin  # GPIO22
DD23: microcontroller.Pin  # GPIO23
D24: microcontroller.Pin  # GPIO24
D25: microcontroller.Pin  # GPIO25
LED: microcontroller.Pin  # GPIO25


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


# Unmapped:
#   none
