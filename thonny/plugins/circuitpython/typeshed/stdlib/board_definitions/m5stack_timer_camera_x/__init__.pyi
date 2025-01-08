# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Timer Camera X
 - port: espressif
 - board_id: m5stack_timer_camera_x
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # GPIO2
G4: microcontroller.Pin  # GPIO4
G13: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO13
BAT_HOLD: microcontroller.Pin  # GPIO33
BAT_ADC: microcontroller.Pin  # GPIO38
BM8563_SCL: microcontroller.Pin  # GPIO14
BM8563_SDA: microcontroller.Pin  # GPIO12
VSYNC: microcontroller.Pin  # GPIO22
HREF: microcontroller.Pin  # GPIO26
PCLK: microcontroller.Pin  # GPIO21
XCLK: microcontroller.Pin  # GPIO27
RESET: microcontroller.Pin  # GPIO15
SSCB_SDA: microcontroller.Pin  # GPIO25
SSCB_SCL: microcontroller.Pin  # GPIO23
D9: microcontroller.Pin  # GPIO19
D8: microcontroller.Pin  # GPIO36
D7: microcontroller.Pin  # GPIO18
D6: microcontroller.Pin  # GPIO39
D5: microcontroller.Pin  # GPIO5
D4: microcontroller.Pin  # GPIO34
D3: microcontroller.Pin  # GPIO35
D2: microcontroller.Pin  # GPIO32


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

D: Tuple[Any]


# Unmapped:
#   none
