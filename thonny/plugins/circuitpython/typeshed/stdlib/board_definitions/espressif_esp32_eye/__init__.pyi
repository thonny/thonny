# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Espressif ESP32-EYE
 - port: espressif
 - board_id: espressif_esp32_eye
 - NVM size: 8192
 - Included modules: _asyncio, adafruit_bus_device, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
I2S_SCK: microcontroller.Pin  # GPIO26
I2S_WS: microcontroller.Pin  # GPIO32
I2S_SDO: microcontroller.Pin  # GPIO32
BOOT: microcontroller.Pin  # GPIO0
BUTTON: microcontroller.Pin  # GPIO15
LED_RED: microcontroller.Pin  # GPIO21
LED_WHITE: microcontroller.Pin  # GPIO22
CAMERA_VSYNC: microcontroller.Pin  # GPIO5
CAMERA_HREF: microcontroller.Pin  # GPIO27
CAMERA_PCLK: microcontroller.Pin  # GPIO25
CAMERA_XCLK: microcontroller.Pin  # GPIO4


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

CAMERA_DATA: Tuple[Any]


# Unmapped:
#   none
