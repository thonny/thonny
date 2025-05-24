# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Camera
 - port: espressif
 - board_id: adafruit_esp32s3_camera
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, os, os.getenv, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rtc, sdcardio, sdioio, select, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
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
MOSI: microcontroller.Pin  # GPIO35
SCK: microcontroller.Pin  # GPIO36
MISO: microcontroller.Pin  # GPIO37
TFT_RESET: microcontroller.Pin  # GPIO38
TFT_CS: microcontroller.Pin  # GPIO39
TFT_DC: microcontroller.Pin  # GPIO40
TFT_BACKLIGHT: microcontroller.Pin  # GPIO45
CARD_CS: microcontroller.Pin  # GPIO48
MIC: microcontroller.Pin  # GPIO2
IRQ: microcontroller.Pin  # GPIO3
NEOPIXEL: microcontroller.Pin  # GPIO1
SPEAKER: microcontroller.Pin  # GPIO46
BUTTON: microcontroller.Pin  # GPIO0
BATTERY_MONITOR: microcontroller.Pin  # GPIO4
A0: microcontroller.Pin  # GPIO17
A1: microcontroller.Pin  # GPIO18
SDA: microcontroller.Pin  # GPIO34
SCL: microcontroller.Pin  # GPIO33
CAMERA_VSYNC: microcontroller.Pin  # GPIO5
CAMERA_HREF: microcontroller.Pin  # GPIO6
CAMERA_DATA9: microcontroller.Pin  # GPIO7
CAMERA_XCLK: microcontroller.Pin  # GPIO8
CAMERA_DATA8: microcontroller.Pin  # GPIO9
CAMERA_DATA7: microcontroller.Pin  # GPIO10
CAMERA_PCLK: microcontroller.Pin  # GPIO11
CAMERA_DATA6: microcontroller.Pin  # GPIO12
CAMERA_DATA2: microcontroller.Pin  # GPIO13
CAMERA_DATA5: microcontroller.Pin  # GPIO14
CAMERA_DATA3: microcontroller.Pin  # GPIO15
CAMERA_DATA4: microcontroller.Pin  # GPIO16
CAMERA_RESET: microcontroller.Pin  # GPIO47
CAMERA_PWDN: microcontroller.Pin  # GPIO21


# Members:
CAMERA_DATA: Tuple[Any]

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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
