# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Oxocard Artwork
 - port: espressif
 - board_id: oxocard_artwork
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BTN5: microcontroller.Pin  # GPIO0
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
AUDIO_N: microcontroller.Pin  # GPIO26
AUDIO_P: microcontroller.Pin  # GPIO25
AUDIO_SD: microcontroller.Pin  # GPIO20
LCD_LED: microcontroller.Pin  # GPIO19
LCD_DC: microcontroller.Pin  # GPIO27
LCD_CS: microcontroller.Pin  # GPIO15
LCD_RST: microcontroller.Pin  # GPIO4
MISO: microcontroller.Pin  # GPIO8
MOSI: microcontroller.Pin  # GPIO5
SCK: microcontroller.Pin  # GPIO7
BTN4: microcontroller.Pin  # GPIO39
BTN3: microcontroller.Pin  # GPIO38
BTN2: microcontroller.Pin  # GPIO37
BTN1: microcontroller.Pin  # GPIO36
ACC_INT1: microcontroller.Pin  # GPIO34
ACC_INT2: microcontroller.Pin  # GPIO35


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display

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
