# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for DFRobot FireBeetle 2 ESP32-S3
 - port: espressif
 - board_id: firebeetle2_esp32s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: AXP313A
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
IO17: microcontroller.Pin  # GPIO17
SCK: microcontroller.Pin  # GPIO17
IO15: microcontroller.Pin  # GPIO15
MOSI: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
MISO: microcontroller.Pin  # GPIO16
IO2: microcontroller.Pin  # GPIO2
SCL: microcontroller.Pin  # GPIO2
IO1: microcontroller.Pin  # GPIO1
SDA: microcontroller.Pin  # GPIO1
IO0: microcontroller.Pin  # GPIO0
D9: microcontroller.Pin  # GPIO0
BOOT: microcontroller.Pin  # GPIO0
IO9: microcontroller.Pin  # GPIO9
D7: microcontroller.Pin  # GPIO9
IO18: microcontroller.Pin  # GPIO18
D6: microcontroller.Pin  # GPIO18
IO7: microcontroller.Pin  # GPIO7
D5: microcontroller.Pin  # GPIO7
IO38: microcontroller.Pin  # GPIO38
D3: microcontroller.Pin  # GPIO38
IO3: microcontroller.Pin  # GPIO3
D2: microcontroller.Pin  # GPIO3
IO43: microcontroller.Pin  # GPIO43
TXD: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
RXD: microcontroller.Pin  # GPIO44
IO47: microcontroller.Pin  # GPIO47
D14: microcontroller.Pin  # GPIO47
PWR: microcontroller.Pin  # GPIO47
IO11: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
IO10: microcontroller.Pin  # GPIO10
A4: microcontroller.Pin  # GPIO10
IO8: microcontroller.Pin  # GPIO8
A3: microcontroller.Pin  # GPIO8
IO6: microcontroller.Pin  # GPIO6
A2: microcontroller.Pin  # GPIO6
IO5: microcontroller.Pin  # GPIO5
A1: microcontroller.Pin  # GPIO5
IO4: microcontroller.Pin  # GPIO4
A0: microcontroller.Pin  # GPIO4
IO21: microcontroller.Pin  # GPIO21
D13: microcontroller.Pin  # GPIO21
LED: microcontroller.Pin  # GPIO21
IO12: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO11: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
D10: microcontroller.Pin  # GPIO14
CAM_VSYNC: microcontroller.Pin  # GPIO6
CAM_HREF: microcontroller.Pin  # GPIO42
CAM_PCLK: microcontroller.Pin  # GPIO5
CAM_XCLK: microcontroller.Pin  # GPIO45


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

CAM_DATA: Tuple[Any]


# Unmapped:
#   none
