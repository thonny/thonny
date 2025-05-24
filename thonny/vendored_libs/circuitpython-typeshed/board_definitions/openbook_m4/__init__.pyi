# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for The Open Book Feather
 - port: atmel-samd
 - board_id: openbook_m4
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, spitarget, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PB08
A3: microcontroller.Pin  # PB09
A4: microcontroller.Pin  # PA04
A5: microcontroller.Pin  # PA06
A6: microcontroller.Pin  # PB01
A7: microcontroller.Pin  # PB04
A8: microcontroller.Pin  # PB03
A9: microcontroller.Pin  # PB02
A10: microcontroller.Pin  # PA07
A11: microcontroller.Pin  # PB00
D0: microcontroller.Pin  # PB17
D1: microcontroller.Pin  # PB16
D2: microcontroller.Pin  # PB03
D3: microcontroller.Pin  # PB02
D5: microcontroller.Pin  # PA16
D6: microcontroller.Pin  # PA18
D9: microcontroller.Pin  # PA19
D10: microcontroller.Pin  # PA20
D11: microcontroller.Pin  # PA21
D12: microcontroller.Pin  # PA22
D13: microcontroller.Pin  # PA23
LED: microcontroller.Pin  # PA23
D48: microcontroller.Pin  # PB31
RX: microcontroller.Pin  # PB17
TX: microcontroller.Pin  # PB16
SDA: microcontroller.Pin  # PA12
SCL: microcontroller.Pin  # PA13
SCK: microcontroller.Pin  # PA17
MISO: microcontroller.Pin  # PB22
MOSI: microcontroller.Pin  # PB23
SCK1: microcontroller.Pin  # PB13
MOSI1: microcontroller.Pin  # PB15
ECS: microcontroller.Pin  # PB07
EDC: microcontroller.Pin  # PB05
ERST: microcontroller.Pin  # PA00
EBSY: microcontroller.Pin  # PA01
BATTERY: microcontroller.Pin  # PB01
USB: microcontroller.Pin  # PB00
MICIN: microcontroller.Pin  # PB04
MICOUT: microcontroller.Pin  # PA07
NEOPIXEL: microcontroller.Pin  # PA15
LOCK_BUTTON: microcontroller.Pin  # PA27
BUTTON_LATCH: microcontroller.Pin  # PB12
BUTTON_OUT: microcontroller.Pin  # PB30
BUTTON_CLOCK: microcontroller.Pin  # PB14
SDCS: microcontroller.Pin  # PA14
MIC_SHUTDOWN: microcontroller.Pin  # PB31
BCS: microcontroller.Pin  # PB06


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

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
