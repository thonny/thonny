# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Fluff M0
 - port: atmel-samd
 - board_id: fluff_m0
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
AREF: microcontroller.Pin  # PA03
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA06
A2: microcontroller.Pin  # PA08
A3: microcontroller.Pin  # PA04
A4: microcontroller.Pin  # PA05
A5: microcontroller.Pin  # PA09
A6: microcontroller.Pin  # PA07
SCK: microcontroller.Pin  # PA31
MOSI: microcontroller.Pin  # PA00
SDO: microcontroller.Pin  # PA00
MISO: microcontroller.Pin  # PA30
SDI: microcontroller.Pin  # PA30
D0: microcontroller.Pin  # PA11
RX: microcontroller.Pin  # PA11
D1: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA10
SDA: microcontroller.Pin  # PA22
SCL: microcontroller.Pin  # PA23
D5: microcontroller.Pin  # PA15
D6: microcontroller.Pin  # PA01
D9: microcontroller.Pin  # PA14
D10: microcontroller.Pin  # PA18
D11: microcontroller.Pin  # PA16
D12: microcontroller.Pin  # PA19
D13: microcontroller.Pin  # PA17
D14: microcontroller.Pin  # PA27
EN: microcontroller.Pin  # PA27
LED: microcontroller.Pin  # PA28


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
