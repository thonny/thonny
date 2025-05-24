# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Cytron Maker Feather AIoT S3
 - port: espressif
 - board_id: cytron_maker_feather_aiot_s3
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
BOOT: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
LED: microcontroller.Pin  # GPIO2
L: microcontroller.Pin  # GPIO2
LED_BUILTIN: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
BUTTON: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
A4: microcontroller.Pin  # GPIO4
T4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
A3: microcontroller.Pin  # GPIO5
T5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
A2: microcontroller.Pin  # GPIO6
T6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
SS: microcontroller.Pin  # GPIO7
A5: microcontroller.Pin  # GPIO7
T7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
MOSI: microcontroller.Pin  # GPIO8
A7: microcontroller.Pin  # GPIO8
T8: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
A1: microcontroller.Pin  # GPIO9
T9: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
A0: microcontroller.Pin  # GPIO10
T10: microcontroller.Pin  # GPIO10
D10: microcontroller.Pin  # GPIO10
VP_EN: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
BUZZER: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
VIN: microcontroller.Pin  # GPIO13
VBATT: microcontroller.Pin  # GPIO13
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO13
A12: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
A11: microcontroller.Pin  # GPIO14
T14: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
TX: microcontroller.Pin  # GPIO15
A10: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
RX: microcontroller.Pin  # GPIO16
A9: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
SCK: microcontroller.Pin  # GPIO17
A6: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
MISO: microcontroller.Pin  # GPIO18
A8: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
D21: microcontroller.Pin  # GPIO21
D38: microcontroller.Pin  # GPIO38
D39: microcontroller.Pin  # GPIO39
D40: microcontroller.Pin  # GPIO40
SCL: microcontroller.Pin  # GPIO41
D41: microcontroller.Pin  # GPIO41
SDA: microcontroller.Pin  # GPIO42
D42: microcontroller.Pin  # GPIO42
RGB: microcontroller.Pin  # GPIO46
RGB_BUILTIN: microcontroller.Pin  # GPIO46
NEOPIXEL: microcontroller.Pin  # GPIO46
D46: microcontroller.Pin  # GPIO46
D47: microcontroller.Pin  # GPIO47
D48: microcontroller.Pin  # GPIO48


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
