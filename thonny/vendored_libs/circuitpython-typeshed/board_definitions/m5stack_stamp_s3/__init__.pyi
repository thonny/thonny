# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Stamp-S3
 - port: espressif
 - board_id: m5stack_stamp_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
IO0: microcontroller.Pin  # GPIO0
G0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
G1: microcontroller.Pin  # GPIO1
TCH1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
G2: microcontroller.Pin  # GPIO2
TCH2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO3
G3: microcontroller.Pin  # GPIO3
TCH3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
G4: microcontroller.Pin  # GPIO4
TCH4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
G5: microcontroller.Pin  # GPIO5
TCH5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
G6: microcontroller.Pin  # GPIO6
TCH6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO7
G7: microcontroller.Pin  # GPIO7
TCH7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
A8: microcontroller.Pin  # GPIO8
G8: microcontroller.Pin  # GPIO8
TCH8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
A9: microcontroller.Pin  # GPIO9
G9: microcontroller.Pin  # GPIO9
TCH9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
A10: microcontroller.Pin  # GPIO10
G10: microcontroller.Pin  # GPIO10
TCH10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
A11: microcontroller.Pin  # GPIO11
G11: microcontroller.Pin  # GPIO11
TCH11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
A12: microcontroller.Pin  # GPIO12
G12: microcontroller.Pin  # GPIO12
TCH12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
A13: microcontroller.Pin  # GPIO13
G13: microcontroller.Pin  # GPIO13
TCH13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
A14: microcontroller.Pin  # GPIO14
G14: microcontroller.Pin  # GPIO14
TCH14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
A15: microcontroller.Pin  # GPIO15
G15: microcontroller.Pin  # GPIO15
IO39: microcontroller.Pin  # GPIO39
G39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
G40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
G41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
G42: microcontroller.Pin  # GPIO42
IO43: microcontroller.Pin  # GPIO43
G43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
G44: microcontroller.Pin  # GPIO44
IO46: microcontroller.Pin  # GPIO46
G46: microcontroller.Pin  # GPIO46
I2C_SCL: microcontroller.Pin  # GPIO15
I2C_SDA: microcontroller.Pin  # GPIO13
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
NEOPIXEL: microcontroller.Pin  # GPIO21
TFT_RST: microcontroller.Pin  # GPIO33
TFT_RESET: microcontroller.Pin  # GPIO33
TFT_DC: microcontroller.Pin  # GPIO34
TFT_RS: microcontroller.Pin  # GPIO34
TFT_MOSI: microcontroller.Pin  # GPIO35
TFT_DAT: microcontroller.Pin  # GPIO35
TFT_DATA: microcontroller.Pin  # GPIO35
TFT_SCK: microcontroller.Pin  # GPIO36
TFT_CS: microcontroller.Pin  # GPIO37
TFT_BACKLIGHT: microcontroller.Pin  # GPIO38
TFT_BL: microcontroller.Pin  # GPIO38
IO16: microcontroller.Pin  # GPIO16
G16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
G17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
G18: microcontroller.Pin  # GPIO18


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def TFT_SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
