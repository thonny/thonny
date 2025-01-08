# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for FeatherS2
 - port: espressif
 - board_id: unexpectedmaker_feathers2
 - NVM size: 8192
 - Included modules: _asyncio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO18: microcontroller.Pin  # GPIO18
A1: microcontroller.Pin  # GPIO18
D15: microcontroller.Pin  # GPIO18
DAC2: microcontroller.Pin  # GPIO18
IO17: microcontroller.Pin  # GPIO17
A0: microcontroller.Pin  # GPIO17
D14: microcontroller.Pin  # GPIO17
DAC1: microcontroller.Pin  # GPIO17
IO14: microcontroller.Pin  # GPIO14
A2: microcontroller.Pin  # GPIO14
D16: microcontroller.Pin  # GPIO14
IO12: microcontroller.Pin  # GPIO12
A3: microcontroller.Pin  # GPIO12
D17: microcontroller.Pin  # GPIO12
IO6: microcontroller.Pin  # GPIO6
A4: microcontroller.Pin  # GPIO6
D18: microcontroller.Pin  # GPIO6
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D19: microcontroller.Pin  # GPIO5
IO36: microcontroller.Pin  # GPIO36
SCK: microcontroller.Pin  # GPIO36
D25: microcontroller.Pin  # GPIO36
IO35: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
D24: microcontroller.Pin  # GPIO35
IO37: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO37
D23: microcontroller.Pin  # GPIO37
IO44: microcontroller.Pin  # GPIO44
D0: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
IO43: microcontroller.Pin  # GPIO43
D1: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
SDA: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
D10: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
D11: microcontroller.Pin  # GPIO9
IO0: microcontroller.Pin  # GPIO0
D4: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
D5: microcontroller.Pin  # GPIO1
A10: microcontroller.Pin  # GPIO1
IO3: microcontroller.Pin  # GPIO3
D6: microcontroller.Pin  # GPIO3
A9: microcontroller.Pin  # GPIO3
IO7: microcontroller.Pin  # GPIO7
D9: microcontroller.Pin  # GPIO7
A8: microcontroller.Pin  # GPIO7
IO33: microcontroller.Pin  # GPIO33
D20: microcontroller.Pin  # GPIO33
IO38: microcontroller.Pin  # GPIO38
D21: microcontroller.Pin  # GPIO38
IO10: microcontroller.Pin  # GPIO10
D12: microcontroller.Pin  # GPIO10
A7: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
D13: microcontroller.Pin  # GPIO11
A6: microcontroller.Pin  # GPIO11
LED: microcontroller.Pin  # GPIO13
APA102_MOSI: microcontroller.Pin  # GPIO40
APA102_SCK: microcontroller.Pin  # GPIO45
LDO2: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21
IO4: microcontroller.Pin  # GPIO4
AMB: microcontroller.Pin  # GPIO4


# Members:
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

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
