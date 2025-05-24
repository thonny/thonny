# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32-S3-EYE
 - port: espressif
 - board_id: espressif_esp32s3_eye
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
BOOT: microcontroller.Pin  # GPIO0
BUTTONS: microcontroller.Pin  # GPIO1
MIC_SDO: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO5
CAMERA_VSYNC: microcontroller.Pin  # GPIO6
CAMERA_HREF: microcontroller.Pin  # GPIO7
CAMERA_PCLK: microcontroller.Pin  # GPIO13
BATTERY: microcontroller.Pin  # GPIO14
CAMERA_XCLK: microcontroller.Pin  # GPIO15
MOSI: microcontroller.Pin  # GPIO47
SCK: microcontroller.Pin  # GPIO21
MISO1: microcontroller.Pin  # GPIO40
MOSI1: microcontroller.Pin  # GPIO38
SCK1: microcontroller.Pin  # GPIO39
MIC_SCK: microcontroller.Pin  # GPIO41
MIC_WS: microcontroller.Pin  # GPIO42
LCD_DC: microcontroller.Pin  # GPIO43
LCD_CS: microcontroller.Pin  # GPIO44
BACKLIGHT: microcontroller.Pin  # GPIO48


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
