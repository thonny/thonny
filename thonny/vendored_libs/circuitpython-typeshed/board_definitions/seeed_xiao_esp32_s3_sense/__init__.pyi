# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Seeed Xiao ESP32-S3 Sense
 - port: espressif
 - board_id: seeed_xiao_esp32_s3_sense
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO6
D0: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO43
D7: microcontroller.Pin  # GPIO44
D8: microcontroller.Pin  # GPIO7
D9: microcontroller.Pin  # GPIO8
D10: microcontroller.Pin  # GPIO9
LED: microcontroller.Pin  # GPIO21
SDA: microcontroller.Pin  # GPIO5
SCL: microcontroller.Pin  # GPIO6
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
MOSI: microcontroller.Pin  # GPIO9
MISO: microcontroller.Pin  # GPIO8
SCK: microcontroller.Pin  # GPIO7
SDCS: microcontroller.Pin  # GPIO21
CAM_D0: microcontroller.Pin  # GPIO15
CAM_D1: microcontroller.Pin  # GPIO17
CAM_D2: microcontroller.Pin  # GPIO18
CAM_D3: microcontroller.Pin  # GPIO16
CAM_D4: microcontroller.Pin  # GPIO14
CAM_D5: microcontroller.Pin  # GPIO12
CAM_D6: microcontroller.Pin  # GPIO11
CAM_D7: microcontroller.Pin  # GPIO48
CAM_XCLK: microcontroller.Pin  # GPIO10
CAM_HREF: microcontroller.Pin  # GPIO47
CAM_PCLK: microcontroller.Pin  # GPIO13
CAM_VSYNC: microcontroller.Pin  # GPIO38
CAM_SCL: microcontroller.Pin  # GPIO39
CAM_SDA: microcontroller.Pin  # GPIO40
MIC_DATA: microcontroller.Pin  # GPIO41
MIC_CLK: microcontroller.Pin  # GPIO42


# Members:
CAM_DATA: Tuple[Any]

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
