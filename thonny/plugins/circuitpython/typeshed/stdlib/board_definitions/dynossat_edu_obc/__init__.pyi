# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for DynOSSAT-EDU-OBC
 - port: atmel-samd
 - board_id: dynossat_edu_obc
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA07
A1: microcontroller.Pin  # PA06
A2: microcontroller.Pin  # PA05
A3: microcontroller.Pin  # PA04
A4: microcontroller.Pin  # PB09
A5: microcontroller.Pin  # PB08
SCK: microcontroller.Pin  # PB03
MOSI: microcontroller.Pin  # PB02
MISO: microcontroller.Pin  # PB01
D0: microcontroller.Pin  # PB15
D30: microcontroller.Pin  # PA22
D31: microcontroller.Pin  # PA23
RX: microcontroller.Pin  # PA23
D1: microcontroller.Pin  # PB14
TX: microcontroller.Pin  # PA22
SDA: microcontroller.Pin  # PB12
SCL: microcontroller.Pin  # PB13
D2: microcontroller.Pin  # PB11
D3: microcontroller.Pin  # PB10
D4: microcontroller.Pin  # PA11
D5: microcontroller.Pin  # PA10
D6: microcontroller.Pin  # PA09
D7: microcontroller.Pin  # PB07
D8: microcontroller.Pin  # PB06
D9: microcontroller.Pin  # PB30
D10: microcontroller.Pin  # PA12
D11: microcontroller.Pin  # PA15
D12: microcontroller.Pin  # PB00
D13: microcontroller.Pin  # PA08
D32: microcontroller.Pin  # PA30
D33: microcontroller.Pin  # PA31
SD_CS: microcontroller.Pin  # PB22
INT_IMU: microcontroller.Pin  # PA12
SAT_POWER: microcontroller.Pin  # PA15
OVTEMP: microcontroller.Pin  # PB00
NEOPIXEL: microcontroller.Pin  # PA08


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
