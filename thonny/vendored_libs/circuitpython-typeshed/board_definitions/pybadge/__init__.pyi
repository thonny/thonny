# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Pybadge
 - port: atmel-samd
 - board_id: pybadge
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, frequencyio, getpass, i2ctarget, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: stage, ugame
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
D0: microcontroller.Pin  # PB17
D1: microcontroller.Pin  # PB16
D2: microcontroller.Pin  # PB03
D3: microcontroller.Pin  # PB02
D4: microcontroller.Pin  # PA14
D5: microcontroller.Pin  # PA16
D6: microcontroller.Pin  # PA18
D7: microcontroller.Pin  # PB14
D8: microcontroller.Pin  # PA15
D9: microcontroller.Pin  # PA19
D10: microcontroller.Pin  # PA20
D11: microcontroller.Pin  # PA21
D12: microcontroller.Pin  # PA22
LED: microcontroller.Pin  # PA23
D13: microcontroller.Pin  # PA23
RX: microcontroller.Pin  # PB17
TX: microcontroller.Pin  # PB16
SDA: microcontroller.Pin  # PA12
SCL: microcontroller.Pin  # PA13
SCK: microcontroller.Pin  # PA17
MISO: microcontroller.Pin  # PB22
MOSI: microcontroller.Pin  # PB23
NEOPIXEL: microcontroller.Pin  # PA15
LIGHT: microcontroller.Pin  # PB04
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # PB14
SPEAKER: microcontroller.Pin  # PA02
SPEAKER_ENABLE: microcontroller.Pin  # PA27
BUTTON_LATCH: microcontroller.Pin  # PB00
BUTTON_OUT: microcontroller.Pin  # PB30
BUTTON_CLOCK: microcontroller.Pin  # PB31
TFT_LITE: microcontroller.Pin  # PA01
TFT_MOSI: microcontroller.Pin  # PB15
TFT_SCK: microcontroller.Pin  # PB13
TFT_RST: microcontroller.Pin  # PA00
TFT_CS: microcontroller.Pin  # PB07
TFT_DC: microcontroller.Pin  # PB05


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
