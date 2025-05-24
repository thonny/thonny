# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Trellis M4 Express
 - port: atmel-samd
 - board_id: trellis_m4_express
 - NVM size: 256
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA04
MICOUT: microcontroller.Pin  # PA06
MICIN: microcontroller.Pin  # PA07
SDA: microcontroller.Pin  # PB08
SCL: microcontroller.Pin  # PB09
ACCELEROMETER_SDA: microcontroller.Pin  # PA12
ACCELEROMETER_SCL: microcontroller.Pin  # PA13
COL0: microcontroller.Pin  # PA14
COL1: microcontroller.Pin  # PA15
COL2: microcontroller.Pin  # PA16
COL3: microcontroller.Pin  # PA17
COL4: microcontroller.Pin  # PA20
COL5: microcontroller.Pin  # PA21
COL6: microcontroller.Pin  # PA22
COL7: microcontroller.Pin  # PA23
ROW0: microcontroller.Pin  # PA18
ROW1: microcontroller.Pin  # PA19
ROW2: microcontroller.Pin  # PB22
ROW3: microcontroller.Pin  # PB23
INT: microcontroller.Pin  # PA04
NEOPIXEL: microcontroller.Pin  # PA27
APA102_MOSI: microcontroller.Pin  # PB03
DOTSTAR_DATA: microcontroller.Pin  # PB03
APA102_SCK: microcontroller.Pin  # PB02
DOTSTAR_CLOCK: microcontroller.Pin  # PB02


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
