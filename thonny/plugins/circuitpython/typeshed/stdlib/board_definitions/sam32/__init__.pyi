# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SAM32v26
 - port: atmel-samd
 - board_id: sam32
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO39: microcontroller.Pin  # PB08
IO36: microcontroller.Pin  # PB09
A6: microcontroller.Pin  # PB04
A7: microcontroller.Pin  # PB05
A8: microcontroller.Pin  # PB06
A9: microcontroller.Pin  # PB07
SCK: microcontroller.Pin  # PB13
MOSI: microcontroller.Pin  # PB12
MISO: microcontroller.Pin  # PB14
xSDCS: microcontroller.Pin  # PA04
DAC0: microcontroller.Pin  # PA02
DAC1: microcontroller.Pin  # PA05
D16: microcontroller.Pin  # PA07
D19: microcontroller.Pin  # PA10
D20: microcontroller.Pin  # PA11
D31: microcontroller.Pin  # PA14
D35: microcontroller.Pin  # PA16
D36: microcontroller.Pin  # PA17
D37: microcontroller.Pin  # PA18
D38: microcontroller.Pin  # PA19
D41: microcontroller.Pin  # PA20
D42: microcontroller.Pin  # PA21
D43: microcontroller.Pin  # PA22
D44: microcontroller.Pin  # PA23
D49: microcontroller.Pin  # PB22
D50: microcontroller.Pin  # PB23
D59: microcontroller.Pin  # PB30
D60: microcontroller.Pin  # PB31
D61: microcontroller.Pin  # PB00
IO13: microcontroller.Pin  # PB01
IO12: microcontroller.Pin  # PB02
IO14: microcontroller.Pin  # PB03
TCK: microcontroller.Pin  # PB01
TDI: microcontroller.Pin  # PB02
TMS: microcontroller.Pin  # PB03
ESP_CS: microcontroller.Pin  # PB15
TX1: microcontroller.Pin  # PA12
RX1: microcontroller.Pin  # PA13
TX2: microcontroller.Pin  # PB16
RX2: microcontroller.Pin  # PB17
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09
RTS: microcontroller.Pin  # PB11
DTR: microcontroller.Pin  # PB10
LED: microcontroller.Pin  # PA27
NEOPIXEL: microcontroller.Pin  # PA15
BATTERY: microcontroller.Pin  # PA06


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
