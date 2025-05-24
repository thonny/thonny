# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Gemma M0
 - port: atmel-samd
 - board_id: gemma_m0
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
A1: microcontroller.Pin  # PA05
D2: microcontroller.Pin  # PA05
RX: microcontroller.Pin  # PA05
SCL: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA04
D0: microcontroller.Pin  # PA04
TX: microcontroller.Pin  # PA04
SDA: microcontroller.Pin  # PA04
A0: microcontroller.Pin  # PA02
D1: microcontroller.Pin  # PA02
LED: microcontroller.Pin  # PA23
L: microcontroller.Pin  # PA23
D13: microcontroller.Pin  # PA23
APA102_MOSI: microcontroller.Pin  # PA00
DOTSTAR_DATA: microcontroller.Pin  # PA00
APA102_SCK: microcontroller.Pin  # PA01
DOTSTAR_CLOCK: microcontroller.Pin  # PA01


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
