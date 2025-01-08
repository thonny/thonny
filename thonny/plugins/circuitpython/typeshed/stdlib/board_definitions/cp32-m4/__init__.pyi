# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for CP32-M4
 - port: atmel-samd
 - board_id: cp32-m4
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
SPEAKER_P: microcontroller.Pin  # PA02
SPEAKER_N: microcontroller.Pin  # PA05
BATTERY: microcontroller.Pin  # PA04
STATUS_LED: microcontroller.Pin  # PA15
BACKLIGHT_PWM: microcontroller.Pin  # PB09
SW1_2: microcontroller.Pin  # PA06
SW3_4: microcontroller.Pin  # PB08
SW5: microcontroller.Pin  # PB12
SW7: microcontroller.Pin  # PB06
SW8: microcontroller.Pin  # PB03
SW9: microcontroller.Pin  # PB05
SW10: microcontroller.Pin  # PB04
EXT_HDR3: microcontroller.Pin  # PB07
EXT_HDR4: microcontroller.Pin  # PA20
EXT_HDR5: microcontroller.Pin  # PA22
EXT_SW6: microcontroller.Pin  # PA21
SD0: microcontroller.Pin  # PA16
SD1: microcontroller.Pin  # PA18
SD2: microcontroller.Pin  # PB13
SD3: microcontroller.Pin  # PB14
CMD: microcontroller.Pin  # PB15
CLK: microcontroller.Pin  # PA14
TX: microcontroller.Pin  # PB16
RX: microcontroller.Pin  # PB17
VSPI_SCK: microcontroller.Pin  # PA17
VSPI_MOSI: microcontroller.Pin  # PB23
VSPI_MISO: microcontroller.Pin  # PB22
VSPI_CS0: microcontroller.Pin  # PA19
VSPI_CS1: microcontroller.Pin  # PA27
LCD_DC: microcontroller.Pin  # PA23
APA102_SCK: microcontroller.Pin  # PA17
APA102_MOSI: microcontroller.Pin  # PA12


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
