# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Spotpear ESP32C3 LCD 1.69
 - port: espressif
 - board_id: spotpear_esp32c3_lcd_1_69
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BOOT: microcontroller.Pin  # GPIO9
BUTTON0: microcontroller.Pin  # GPIO9
BUZZER: microcontroller.Pin  # GPIO1
SCK: microcontroller.Pin  # GPIO5
MISO: microcontroller.Pin  # GPIO4
MOSI: microcontroller.Pin  # GPIO6
LCD_DC: microcontroller.Pin  # GPIO2
LCD_CS: microcontroller.Pin  # GPIO3
LCD_RST: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO7
SDA: microcontroller.Pin  # GPIO11
TOUCH_INT: microcontroller.Pin  # GPIO9
TOUCH_RST: microcontroller.Pin  # GPIO10
RX: microcontroller.Pin  # GPIO20
IO20: microcontroller.Pin  # GPIO20
TX: microcontroller.Pin  # GPIO21
IO21: microcontroller.Pin  # GPIO21


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
