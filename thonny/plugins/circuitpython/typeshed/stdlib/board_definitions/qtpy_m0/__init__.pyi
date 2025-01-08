# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit QT Py M0
 - port: atmel-samd
 - board_id: qtpy_m0
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
D0: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA02
D1: microcontroller.Pin  # PA03
A1: microcontroller.Pin  # PA03
D2: microcontroller.Pin  # PA04
A2: microcontroller.Pin  # PA04
D3: microcontroller.Pin  # PA05
A3: microcontroller.Pin  # PA05
D4: microcontroller.Pin  # PA16
SDA: microcontroller.Pin  # PA16
D5: microcontroller.Pin  # PA17
SCL: microcontroller.Pin  # PA17
D6: microcontroller.Pin  # PA06
A6: microcontroller.Pin  # PA06
TX: microcontroller.Pin  # PA06
D7: microcontroller.Pin  # PA07
A7: microcontroller.Pin  # PA07
RX: microcontroller.Pin  # PA07
D8: microcontroller.Pin  # PA11
A8: microcontroller.Pin  # PA11
SCK: microcontroller.Pin  # PA11
D9: microcontroller.Pin  # PA09
A9: microcontroller.Pin  # PA09
MISO: microcontroller.Pin  # PA09
D10: microcontroller.Pin  # PA10
A10: microcontroller.Pin  # PA10
MOSI: microcontroller.Pin  # PA10
NEOPIXEL: microcontroller.Pin  # PA18
NEOPIXEL_POWER: microcontroller.Pin  # PA15


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


# Unmapped:
#   none
