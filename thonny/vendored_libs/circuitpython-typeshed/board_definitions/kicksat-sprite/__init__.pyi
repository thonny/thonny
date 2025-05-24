# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Sprite_v2b
 - port: atmel-samd
 - board_id: kicksat-sprite
 - NVM size: 256
 - Included modules: _asyncio, adafruit_bus_device, alarm, analogio, array, atexit, binascii, bitbangio, board, builtins, builtins.pow3, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, errno, frequencyio, i2ctarget, io, json, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, random, re, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, sys, time, traceback, usb_cdc, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SCK: microcontroller.Pin  # PA05
MOSI: microcontroller.Pin  # PA07
MISO: microcontroller.Pin  # PA04
radioCS: microcontroller.Pin  # PA00
WAKE: microcontroller.Pin  # PA01
SHDWN: microcontroller.Pin  # PB10
PWDWN: microcontroller.Pin  # PB11
TST: microcontroller.Pin  # PA11
FSYNC: microcontroller.Pin  # PA13
VCLK: microcontroller.Pin  # PA14
FSYNC: microcontroller.Pin  # PA15
MD: microcontroller.Pin  # PA18
MC: microcontroller.Pin  # PA19
PA08: microcontroller.Pin  # PA08
PA10: microcontroller.Pin  # PA10
PA09: microcontroller.Pin  # PA09
PA06: microcontroller.Pin  # PA06
DAC0: microcontroller.Pin  # PA02
TX: microcontroller.Pin  # PB09
RX: microcontroller.Pin  # PB08
SDA: microcontroller.Pin  # PA16
SCL: microcontroller.Pin  # PA17
LED: microcontroller.Pin  # PB03


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
