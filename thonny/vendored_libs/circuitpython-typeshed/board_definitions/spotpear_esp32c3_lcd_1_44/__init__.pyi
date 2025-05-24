# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Spotpear ESP32C3 LCD 1.44
 - port: espressif
 - board_id: spotpear_esp32c3_lcd_1_44
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
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
BUTTON1: microcontroller.Pin  # GPIO8
BUTTON2: microcontroller.Pin  # GPIO10
LED: microcontroller.Pin  # GPIO11
LCD_MOSI: microcontroller.Pin  # GPIO4
LCD_SCK: microcontroller.Pin  # GPIO3
LCD_DC: microcontroller.Pin  # GPIO0
LCD_RST: microcontroller.Pin  # GPIO5
LCD_CS: microcontroller.Pin  # GPIO2
RX: microcontroller.Pin  # GPIO20
TX: microcontroller.Pin  # GPIO21
IO1: microcontroller.Pin  # GPIO1
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21


# Members:
def LCD_SPI() -> busio.SPI:
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
