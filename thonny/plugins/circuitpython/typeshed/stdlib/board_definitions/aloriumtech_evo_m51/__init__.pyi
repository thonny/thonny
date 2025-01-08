# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for AloriumTech Evo M51
 - port: atmel-samd
 - board_id: aloriumtech_evo_m51
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
D14: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
D15: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PB08
D16: microcontroller.Pin  # PB08
A3: microcontroller.Pin  # PB09
D17: microcontroller.Pin  # PB09
A4: microcontroller.Pin  # PA04
D18: microcontroller.Pin  # PA04
A5: microcontroller.Pin  # PA06
D19: microcontroller.Pin  # PA06
SCK: microcontroller.Pin  # PA17
D25: microcontroller.Pin  # PA17
MOSI: microcontroller.Pin  # PB23
D24: microcontroller.Pin  # PB23
MISO: microcontroller.Pin  # PB22
D23: microcontroller.Pin  # PB22
D0: microcontroller.Pin  # PB17
RX: microcontroller.Pin  # PB17
D1: microcontroller.Pin  # PB16
TX: microcontroller.Pin  # PB16
SDA: microcontroller.Pin  # PA12
SCL: microcontroller.Pin  # PA13
D4: microcontroller.Pin  # PA14
D5: microcontroller.Pin  # PA16
D6: microcontroller.Pin  # PA18
D9: microcontroller.Pin  # PA19
D10: microcontroller.Pin  # PA20
D11: microcontroller.Pin  # PA21
D12: microcontroller.Pin  # PA22
D13: microcontroller.Pin  # PA23
NEOPIXEL: microcontroller.Pin  # PB03
VOLTAGE_MONITOR: microcontroller.Pin  # PB01
BATTERY: microcontroller.Pin  # PB01
SDA_1: microcontroller.Pin  # PD09
SCL_1: microcontroller.Pin  # PD08


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
