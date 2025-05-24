# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare ESP32-C6 LCD 1.47
 - port: espressif
 - board_id: waveshare_esp32_c6_lcd_1_47
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO0
IO0: microcontroller.Pin  # GPIO0
SCL: microcontroller.Pin  # GPIO0
A1: microcontroller.Pin  # GPIO1
IO1: microcontroller.Pin  # GPIO1
SDA: microcontroller.Pin  # GPIO1
A2: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO2
A3: microcontroller.Pin  # GPIO3
IO3: microcontroller.Pin  # GPIO3
A4: microcontroller.Pin  # GPIO4
IO4: microcontroller.Pin  # GPIO4
SD_CS: microcontroller.Pin  # GPIO4
A5: microcontroller.Pin  # GPIO5
IO5: microcontroller.Pin  # GPIO5
MISO: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
BUTTON: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO23: microcontroller.Pin  # GPIO23
RX: microcontroller.Pin  # GPIO17
IO17: microcontroller.Pin  # GPIO17
TX: microcontroller.Pin  # GPIO16
IO16: microcontroller.Pin  # GPIO16
TFT_CS: microcontroller.Pin  # GPIO14
TFT_DC: microcontroller.Pin  # GPIO15
TFT_RESET: microcontroller.Pin  # GPIO21
TFT_BACKLIGHT: microcontroller.Pin  # GPIO22
NEOPIXEL: microcontroller.Pin  # GPIO8


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
