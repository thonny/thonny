# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit FunHouse
 - port: espressif
 - board_id: adafruit_funhouse
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, errno, espidf, espnow, espulp, fontio, fourwire, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, select, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TFT_BACKLIGHT: microcontroller.Pin  # GPIO21
TFT_CS: microcontroller.Pin  # GPIO40
TFT_DC: microcontroller.Pin  # GPIO39
TFT_MOSI: microcontroller.Pin  # GPIO35
TFT_RESET: microcontroller.Pin  # GPIO41
TFT_SCK: microcontroller.Pin  # GPIO36
BUTTON_DOWN: microcontroller.Pin  # GPIO3
BUTTON_SELECT: microcontroller.Pin  # GPIO4
BUTTON_UP: microcontroller.Pin  # GPIO5
CAP6: microcontroller.Pin  # GPIO6
CAP7: microcontroller.Pin  # GPIO7
CAP8: microcontroller.Pin  # GPIO8
CAP9: microcontroller.Pin  # GPIO9
CAP10: microcontroller.Pin  # GPIO10
CAP11: microcontroller.Pin  # GPIO11
CAP12: microcontroller.Pin  # GPIO12
CAP13: microcontroller.Pin  # GPIO13
DOTSTAR_DATA: microcontroller.Pin  # GPIO14
DOTSTAR_CLOCK: microcontroller.Pin  # GPIO15
PIR_SENSE: microcontroller.Pin  # GPIO16
LIGHT: microcontroller.Pin  # GPIO18
SPEAKER: microcontroller.Pin  # GPIO42
LED: microcontroller.Pin  # GPIO37
A0: microcontroller.Pin  # GPIO17
A1: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO1
SCL: microcontroller.Pin  # GPIO33
SDA: microcontroller.Pin  # GPIO34
DEBUG_TX: microcontroller.Pin  # GPIO43
DEBUG_RX: microcontroller.Pin  # GPIO44


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
