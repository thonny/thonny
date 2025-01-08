# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Maker badge by Czech maker
 - port: espressif
 - board_id: maker_badge
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_bus_device, adafruit_connection_manager, adafruit_display_text, adafruit_register, adafruit_requests, adafruit_ssd1680, adafruit_uc8151d, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
CAP5: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO2
CAP4: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO3
CAP3: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO4
CAP2: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
CAP1: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO6
BATTERY: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO8
SDA: microcontroller.Pin  # GPIO8
D9: microcontroller.Pin  # GPIO9
SCL: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
D12: microcontroller.Pin  # GPIO12
D13: microcontroller.Pin  # GPIO13
D14: microcontroller.Pin  # GPIO14
A4: microcontroller.Pin  # GPIO14
D15: microcontroller.Pin  # GPIO15
A3: microcontroller.Pin  # GPIO15
D16: microcontroller.Pin  # GPIO16
A2: microcontroller.Pin  # GPIO16
D17: microcontroller.Pin  # GPIO17
A1: microcontroller.Pin  # GPIO17
D18: microcontroller.Pin  # GPIO18
NEOPIXEL: microcontroller.Pin  # GPIO18
D21: microcontroller.Pin  # GPIO21
NEOPIXEL_POWER: microcontroller.Pin  # GPIO21
NEOPIXEL_POWER_INVERTED: microcontroller.Pin  # GPIO21
D26: microcontroller.Pin  # GPIO26
D33: microcontroller.Pin  # GPIO33
D34: microcontroller.Pin  # GPIO34
D35: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
D36: microcontroller.Pin  # GPIO36
SCK: microcontroller.Pin  # GPIO36
D37: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO37
D38: microcontroller.Pin  # GPIO38
D39: microcontroller.Pin  # GPIO39
D40: microcontroller.Pin  # GPIO40
D41: microcontroller.Pin  # GPIO41
D42: microcontroller.Pin  # GPIO42


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
