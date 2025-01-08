# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Ai Thinker ESP32-CAM
 - port: espressif
 - board_id: ai-thinker-esp32-cam
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # GPIO33
LED_INVERTED: microcontroller.Pin  # GPIO33
FLASHLIGHT: microcontroller.Pin  # GPIO4
BUTTON: microcontroller.Pin  # GPIO0
SDIO_CLK: microcontroller.Pin  # GPIO14
SDIO_CMD: microcontroller.Pin  # GPIO15
SDIO_D0: microcontroller.Pin  # GPIO2
SDIO_D1: microcontroller.Pin  # GPIO4
SDIO_D2: microcontroller.Pin  # GPIO12
SDIO_D3: microcontroller.Pin  # GPIO13
SD_SCK: microcontroller.Pin  # GPIO14
SD_MOSI: microcontroller.Pin  # GPIO15
SD_MISO: microcontroller.Pin  # GPIO2
SD_CS: microcontroller.Pin  # GPIO13
CAMERA_DATA2: microcontroller.Pin  # GPIO5
CAMERA_DATA3: microcontroller.Pin  # GPIO18
CAMERA_DATA4: microcontroller.Pin  # GPIO19
CAMERA_DATA5: microcontroller.Pin  # GPIO21
CAMERA_DATA6: microcontroller.Pin  # GPIO36
CAMERA_DATA7: microcontroller.Pin  # GPIO39
CAMERA_DATA8: microcontroller.Pin  # GPIO34
CAMERA_DATA9: microcontroller.Pin  # GPIO35
CAMERA_HREF: microcontroller.Pin  # GPIO23
CAMERA_PCLK: microcontroller.Pin  # GPIO22
CAMERA_PWDN: microcontroller.Pin  # GPIO32
CAMERA_VSYNC: microcontroller.Pin  # GPIO25
CAMERA_XCLK: microcontroller.Pin  # GPIO0
CAMERA_SIOD: microcontroller.Pin  # GPIO26
CAMERA_SIOC: microcontroller.Pin  # GPIO27
U0R: microcontroller.Pin  # GPIO3
U0T: microcontroller.Pin  # GPIO1
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO3: microcontroller.Pin  # GPIO3
IO16: microcontroller.Pin  # GPIO16
IO2: microcontroller.Pin  # GPIO2
IO4: microcontroller.Pin  # GPIO4
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO13


# Members:
def SD_SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

CAMERA_DATA: Tuple[Any]

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
