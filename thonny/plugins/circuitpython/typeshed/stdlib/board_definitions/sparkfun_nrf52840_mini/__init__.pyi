# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun Pro nRF52840 Mini
 - port: nordic
 - board_id: sparkfun_nrf52840_mini
 - NVM size: 8192
 - Included modules: _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # P1_15
D1: microcontroller.Pin  # P0_17
D3: microcontroller.Pin  # P0_19
D4: microcontroller.Pin  # P0_20
D5: microcontroller.Pin  # P0_21
D6: microcontroller.Pin  # P0_22
D7: microcontroller.Pin  # P0_23
D8: microcontroller.Pin  # P0_09
D9: microcontroller.Pin  # P0_10
D10: microcontroller.Pin  # P0_02
D11: microcontroller.Pin  # P0_03
D12: microcontroller.Pin  # P0_31
D13: microcontroller.Pin  # P0_30
D14: microcontroller.Pin  # P0_29
D15: microcontroller.Pin  # P0_28
D16: microcontroller.Pin  # P0_05
D17: microcontroller.Pin  # P0_04
A0: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_03
A2: microcontroller.Pin  # P0_04
A3: microcontroller.Pin  # P0_05
A4: microcontroller.Pin  # P0_28
A5: microcontroller.Pin  # P0_29
A6: microcontroller.Pin  # P0_30
A7: microcontroller.Pin  # P0_31
SDA: microcontroller.Pin  # P0_08
SCL: microcontroller.Pin  # P0_11
MISO: microcontroller.Pin  # P0_31
MOSI: microcontroller.Pin  # P0_03
SCK: microcontroller.Pin  # P0_30
LED1: microcontroller.Pin  # P0_07
BUTTON1: microcontroller.Pin  # P0_13
RX: microcontroller.Pin  # P0_15
TX: microcontroller.Pin  # P0_17


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def QWIIC() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

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
