# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for NanoS3
 - port: espressif
 - board_id: unexpectedmaker_nanos3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
A0: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
A1: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
A2: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
A3: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
A4: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
A5: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
A6: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
SDA: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
A7: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
A8: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
A9: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
A10: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
A11: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
A12: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
A13: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
A14: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
A15: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
A16: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
A17: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
IO21: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
IO33: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
IO34: microcontroller.Pin  # GPIO34
D34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
MO: microcontroller.Pin  # GPIO35
SDO: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
IO37: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO37
MI: microcontroller.Pin  # GPIO37
SDI: microcontroller.Pin  # GPIO37
D37: microcontroller.Pin  # GPIO37
IO36: microcontroller.Pin  # GPIO36
SCK: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
IO43: microcontroller.Pin  # GPIO43
D43: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
D44: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
NEOPIXEL_POWER: microcontroller.Pin  # GPIO42
NEOPIXEL: microcontroller.Pin  # GPIO41


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
