# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Monster M4SK
 - port: atmel-samd
 - board_id: monster_m4sk
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, errno, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2ctarget, io, jpegio, json, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
SPEAKER: microcontroller.Pin  # PA02
HEADPHONE_LEFT: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA02
HEADPHONE_RIGHT: microcontroller.Pin  # PA05
A1: microcontroller.Pin  # PA05
D2: microcontroller.Pin  # PB08
A2: microcontroller.Pin  # PB08
NOSE: microcontroller.Pin  # PB08
D3: microcontroller.Pin  # PB09
A3: microcontroller.Pin  # PB09
LED: microcontroller.Pin  # PA27
D13: microcontroller.Pin  # PA27
SDA: microcontroller.Pin  # PA00
SCL: microcontroller.Pin  # PA01
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # PA22
SPEAKER_ENABLE: microcontroller.Pin  # PA14
MICROPHONE_CLOCK: microcontroller.Pin  # PA16
MICROPHONE_DATA: microcontroller.Pin  # PA17
RIGHT_TFT_LITE: microcontroller.Pin  # PA23
RIGHT_TFT_MOSI: microcontroller.Pin  # PA12
RIGHT_TFT_SCK: microcontroller.Pin  # PA13
RIGHT_TFT_RST: microcontroller.Pin  # PA04
RIGHT_TFT_CS: microcontroller.Pin  # PA06
RIGHT_TFT_DC: microcontroller.Pin  # PA07
LEFT_TFT_MOSI: microcontroller.Pin  # PB02
LEFT_TFT_SCK: microcontroller.Pin  # PB03
LEFT_TFT_CS: microcontroller.Pin  # PB23
LEFT_TFT_DC: microcontroller.Pin  # PB22


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
RIGHT_DISPLAY: displayio.Display


# Unmapped:
#   none
