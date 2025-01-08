# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack M5Paper
 - port: espressif
 - board_id: m5stack_m5paper
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
POWER_MAIN: microcontroller.Pin  # GPIO2
SD_CS: microcontroller.Pin  # GPIO4
POWER_EXT: microcontroller.Pin  # GPIO5
MOSI: microcontroller.Pin  # GPIO12
MISO: microcontroller.Pin  # GPIO13
SCK: microcontroller.Pin  # GPIO14
IT8951_CS: microcontroller.Pin  # GPIO15
IT8951_RESET: microcontroller.Pin  # GPIO23
IT8951_POWER: microcontroller.Pin  # GPIO23
IT8951_BUSY: microcontroller.Pin  # GPIO27
PORTC_RX: microcontroller.Pin  # GPIO18
RX2: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
PORTC_TX: microcontroller.Pin  # GPIO19
TX2: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
SDA: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
SCL: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
PORTA_SDA: microcontroller.Pin  # GPIO25
D25: microcontroller.Pin  # GPIO25
PORTA_SCL: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
PORTB_IN: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
PORTB_OUT: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
BATTERY_VOLTAGE: microcontroller.Pin  # GPIO35
TOUCH_INT: microcontroller.Pin  # GPIO36
BTN_UP: microcontroller.Pin  # GPIO37
BTN_CENTER: microcontroller.Pin  # GPIO38
BTN_DOWN: microcontroller.Pin  # GPIO39


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
