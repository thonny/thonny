# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for TinyS2
 - port: espressif
 - board_id: unexpectedmaker_tinys2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
D4: microcontroller.Pin  # GPIO0
IO18: microcontroller.Pin  # GPIO18
A1: microcontroller.Pin  # GPIO18
D15: microcontroller.Pin  # GPIO18
DAC2: microcontroller.Pin  # GPIO18
IO17: microcontroller.Pin  # GPIO17
A0: microcontroller.Pin  # GPIO17
D14: microcontroller.Pin  # GPIO17
DAC1: microcontroller.Pin  # GPIO17
IO7: microcontroller.Pin  # GPIO7
D9: microcontroller.Pin  # GPIO7
A8: microcontroller.Pin  # GPIO7
IO6: microcontroller.Pin  # GPIO6
A4: microcontroller.Pin  # GPIO6
D18: microcontroller.Pin  # GPIO6
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D19: microcontroller.Pin  # GPIO5
IO4: microcontroller.Pin  # GPIO4
A9: microcontroller.Pin  # GPIO4
D6: microcontroller.Pin  # GPIO4
IO35: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
SDO: microcontroller.Pin  # GPIO35
D24: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
MISO: microcontroller.Pin  # GPIO36
SDI: microcontroller.Pin  # GPIO36
D25: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
SCK: microcontroller.Pin  # GPIO37
D23: microcontroller.Pin  # GPIO37
IO14: microcontroller.Pin  # GPIO14
A2: microcontroller.Pin  # GPIO14
D16: microcontroller.Pin  # GPIO14
SDA: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
D10: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
D11: microcontroller.Pin  # GPIO9
IO38: microcontroller.Pin  # GPIO38
D21: microcontroller.Pin  # GPIO38
IO33: microcontroller.Pin  # GPIO33
D20: microcontroller.Pin  # GPIO33
IO43: microcontroller.Pin  # GPIO43
D1: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
D0: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
BATTERY: microcontroller.Pin  # GPIO3
VBAT: microcontroller.Pin  # GPIO3
VBAT_SENSE: microcontroller.Pin  # GPIO3
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO3
VBUS: microcontroller.Pin  # GPIO21
VBUS_SENSE: microcontroller.Pin  # GPIO21
NEOPIXEL_POWER: microcontroller.Pin  # GPIO2
NEOPIXEL: microcontroller.Pin  # GPIO1


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
