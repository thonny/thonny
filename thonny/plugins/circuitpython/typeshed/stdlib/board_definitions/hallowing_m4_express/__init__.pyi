# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Hallowing M4 Express
 - port: atmel-samd
 - board_id: hallowing_m4_express
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
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
SPEAKER: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA06
TOUCH1: microcontroller.Pin  # PA06
A3: microcontroller.Pin  # PB09
TOUCH2: microcontroller.Pin  # PB09
A4: microcontroller.Pin  # PB08
TOUCH3: microcontroller.Pin  # PB08
A5: microcontroller.Pin  # PA04
TOUCH4: microcontroller.Pin  # PA04
LIGHT: microcontroller.Pin  # PB04
A7: microcontroller.Pin  # PB04
SCK: microcontroller.Pin  # PA22
MOSI: microcontroller.Pin  # PB23
MISO: microcontroller.Pin  # PB22
D0: microcontroller.Pin  # PB13
RX: microcontroller.Pin  # PB13
D1: microcontroller.Pin  # PB12
TX: microcontroller.Pin  # PB12
SDA: microcontroller.Pin  # PA12
SCL: microcontroller.Pin  # PA13
D4: microcontroller.Pin  # PA14
D5: microcontroller.Pin  # PA16
D6: microcontroller.Pin  # PA17
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # PB15
D7: microcontroller.Pin  # PB15
D9: microcontroller.Pin  # PA18
D10: microcontroller.Pin  # PA19
D11: microcontroller.Pin  # PA20
D12: microcontroller.Pin  # PA21
LED: microcontroller.Pin  # PA23
D13: microcontroller.Pin  # PA23
TFT_BACKLIGHT: microcontroller.Pin  # PB14
TFT_CS: microcontroller.Pin  # PA27
TFT_DC: microcontroller.Pin  # PB31
TFT_RESET: microcontroller.Pin  # PB30
NEOPIXEL: microcontroller.Pin  # PB16
D8: microcontroller.Pin  # PB16
VOLTAGE_MONITOR: microcontroller.Pin  # PB01
A6: microcontroller.Pin  # PB01
BATTERY: microcontroller.Pin  # PB01
D3: microcontroller.Pin  # PB02
EXTERNAL_NEOPIXEL: microcontroller.Pin  # PB02
A9: microcontroller.Pin  # PB02
D2: microcontroller.Pin  # PB03
SENSE: microcontroller.Pin  # PB03
A8: microcontroller.Pin  # PB03
SPEAKER_ENABLE: microcontroller.Pin  # PB05
CAP_PIN: microcontroller.Pin  # PA15


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
