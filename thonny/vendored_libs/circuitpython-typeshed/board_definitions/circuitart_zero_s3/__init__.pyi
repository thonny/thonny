# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for CircuitART Zero S3
 - port: espressif
 - board_id: circuitart_zero_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_ahtx0, adafruit_st7789, neopixel
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
SDA: microcontroller.Pin  # GPIO33
IO33: microcontroller.Pin  # GPIO33
SCL: microcontroller.Pin  # GPIO34
IO34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
SCK: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO37
IO43: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
TFT_CS: microcontroller.Pin  # GPIO39
TFT_DC: microcontroller.Pin  # GPIO5
TFT_RESET: microcontroller.Pin  # GPIO40
CARD_CS: microcontroller.Pin  # GPIO42
LED: microcontroller.Pin  # GPIO46
NEOPIXEL: microcontroller.Pin  # GPIO47
CAM_LDO_EN: microcontroller.Pin  # GPIO21
CAMERA_VSYNC: microcontroller.Pin  # GPIO38
CAMERA_HREF: microcontroller.Pin  # GPIO48
CAMERA_DATA9: microcontroller.Pin  # GPIO14
CAMERA_XCLK: microcontroller.Pin  # GPIO15
CAMERA_DATA8: microcontroller.Pin  # GPIO13
CAMERA_DATA7: microcontroller.Pin  # GPIO11
CAMERA_PCLK: microcontroller.Pin  # GPIO16
CAMERA_DATA6: microcontroller.Pin  # GPIO10
CAMERA_DATA2: microcontroller.Pin  # GPIO6
CAMERA_DATA5: microcontroller.Pin  # GPIO9
CAMERA_DATA3: microcontroller.Pin  # GPIO7
CAMERA_DATA4: microcontroller.Pin  # GPIO8


# Members:
CAMERA_DATA: Tuple[Any]

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
