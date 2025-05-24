# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Metro ESP32S3
 - port: espressif
 - board_id: adafruit_metro_esp32s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO14
IO14: microcontroller.Pin  # GPIO14
A1: microcontroller.Pin  # GPIO15
IO15: microcontroller.Pin  # GPIO15
A2: microcontroller.Pin  # GPIO16
IO16: microcontroller.Pin  # GPIO16
A3: microcontroller.Pin  # GPIO17
IO17: microcontroller.Pin  # GPIO17
A4: microcontroller.Pin  # GPIO18
IO18: microcontroller.Pin  # GPIO18
A5: microcontroller.Pin  # GPIO1
IO1: microcontroller.Pin  # GPIO1
D0: microcontroller.Pin  # GPIO41
RX: microcontroller.Pin  # GPIO41
IO41: microcontroller.Pin  # GPIO41
D1: microcontroller.Pin  # GPIO40
TX: microcontroller.Pin  # GPIO40
IO40: microcontroller.Pin  # GPIO40
D2: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO3
IO3: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO4
IO4: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
IO5: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
IO6: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
IO7: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
D9: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
IO10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
IO11: microcontroller.Pin  # GPIO11
D12: microcontroller.Pin  # GPIO12
IO12: microcontroller.Pin  # GPIO12
D13: microcontroller.Pin  # GPIO13
IO13: microcontroller.Pin  # GPIO13
LED: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO47
IO47: microcontroller.Pin  # GPIO47
SCL: microcontroller.Pin  # GPIO48
IO48: microcontroller.Pin  # GPIO48
SD_CS: microcontroller.Pin  # GPIO45
SCK: microcontroller.Pin  # GPIO39
IO39: microcontroller.Pin  # GPIO39
MOSI: microcontroller.Pin  # GPIO42
IO42: microcontroller.Pin  # GPIO42
MISO: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21
NEOPIXEL: microcontroller.Pin  # GPIO46
IO46: microcontroller.Pin  # GPIO46
DEBUG_RX: microcontroller.Pin  # GPIO44
DEBUG_TX: microcontroller.Pin  # GPIO43


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
