# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for CircuitBrains Deluxe
 - port: atmel-samd
 - board_id: circuitbrains_deluxe_m4
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PB04
A2: microcontroller.Pin  # PB05
A3: microcontroller.Pin  # PB06
A4: microcontroller.Pin  # PB07
A5: microcontroller.Pin  # PB08
A6: microcontroller.Pin  # PB09
A7: microcontroller.Pin  # PA04
A8: microcontroller.Pin  # PA05
A9: microcontroller.Pin  # PA06
A10: microcontroller.Pin  # PA07
A11: microcontroller.Pin  # PB00
A12: microcontroller.Pin  # PB01
D0: microcontroller.Pin  # PA23
RX: microcontroller.Pin  # PA23
D1: microcontroller.Pin  # PA22
TX: microcontroller.Pin  # PA22
D2: microcontroller.Pin  # PA21
D3: microcontroller.Pin  # PA20
D4: microcontroller.Pin  # PB17
D5: microcontroller.Pin  # PB16
D6: microcontroller.Pin  # PA19
D7: microcontroller.Pin  # PA18
D8: microcontroller.Pin  # PA17
D9: microcontroller.Pin  # PA16
D10: microcontroller.Pin  # PA15
D11: microcontroller.Pin  # PB15
D12: microcontroller.Pin  # PB14
D13: microcontroller.Pin  # PB13
STATUS_LED: microcontroller.Pin  # PB13
LED: microcontroller.Pin  # PB13
D14: microcontroller.Pin  # PB12
D15: microcontroller.Pin  # PB31
D16: microcontroller.Pin  # PA27
D17: microcontroller.Pin  # PB23
D18: microcontroller.Pin  # PB22
SDA: microcontroller.Pin  # PB02
SCL: microcontroller.Pin  # PB03
SCK: microcontroller.Pin  # PA13
MOSI: microcontroller.Pin  # PA12
MISO: microcontroller.Pin  # PA14


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
