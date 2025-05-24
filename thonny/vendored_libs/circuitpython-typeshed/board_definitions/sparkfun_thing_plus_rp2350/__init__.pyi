# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun Thing Plus RP2350
 - port: raspberrypi
 - board_id: sparkfun_thing_plus_rp2350
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, cyw43, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
SCK: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
MOSI: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
MISO: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
SDA: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
SCL: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
D9: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
D12: microcontroller.Pin  # GPIO12
D13: microcontroller.Pin  # GPIO13
NEOPIXEL: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
D15: microcontroller.Pin  # GPIO15
D16: microcontroller.Pin  # GPIO16
D17: microcontroller.Pin  # GPIO17
D18: microcontroller.Pin  # GPIO18
D19: microcontroller.Pin  # GPIO19
D20: microcontroller.Pin  # GPIO20
D21: microcontroller.Pin  # GPIO21
D22: microcontroller.Pin  # GPIO22
A0: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
D27: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
D28: microcontroller.Pin  # GPIO28
LED: microcontroller.Pin  # CYW0
VBUS_SENSE: microcontroller.Pin  # CYW2


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
