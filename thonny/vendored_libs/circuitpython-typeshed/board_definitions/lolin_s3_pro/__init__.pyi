# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LOLIN S3 PRO 16MB Flash 8MB PSRAM
 - port: espressif
 - board_id: lolin_s3_pro
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
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
IO8: microcontroller.Pin  # GPIO8
A7: microcontroller.Pin  # GPIO8
SDA: microcontroller.Pin  # GPIO9
D8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
A8: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
A9: microcontroller.Pin  # GPIO10
SCL: microcontroller.Pin  # GPIO10
D10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
MOSI: microcontroller.Pin  # GPIO11
A10: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
SCK: microcontroller.Pin  # GPIO12
A11: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
MISO: microcontroller.Pin  # GPIO13
A12: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
A13: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
TFT_LED: microcontroller.Pin  # GPIO14
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
TFT_RST: microcontroller.Pin  # GPIO21
IO38: microcontroller.Pin  # GPIO38
D38: microcontroller.Pin  # GPIO38
NEOPIXEL: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
D39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
D40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
D41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
D42: microcontroller.Pin  # GPIO42
IO43: microcontroller.Pin  # GPIO43
D43: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
D44: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
IO45: microcontroller.Pin  # GPIO45
TS_CS: microcontroller.Pin  # GPIO45
IO46: microcontroller.Pin  # GPIO46
TF_CS: microcontroller.Pin  # GPIO46
IO47: microcontroller.Pin  # GPIO47
TFT_DC: microcontroller.Pin  # GPIO47
IO48: microcontroller.Pin  # GPIO48
TFT_CS: microcontroller.Pin  # GPIO48


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


# Unmapped:
#   none
