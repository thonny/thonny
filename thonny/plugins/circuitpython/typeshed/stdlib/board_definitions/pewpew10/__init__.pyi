# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PewPew 10.2
 - port: atmel-samd
 - board_id: pewpew10
 - NVM size: 256
 - Included modules: _pew, analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pwmio, rainbowio, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid
 - Frozen libraries: pew
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
_R1: microcontroller.Pin  # PA05
_R2: microcontroller.Pin  # PA11
_R3: microcontroller.Pin  # PA28
_R4: microcontroller.Pin  # PA09
_R5: microcontroller.Pin  # PA16
_R6: microcontroller.Pin  # PA27
_R7: microcontroller.Pin  # PA17
_R8: microcontroller.Pin  # PA22
_C8: microcontroller.Pin  # PA10
_C7: microcontroller.Pin  # PA18
_C6: microcontroller.Pin  # PA19
_C5: microcontroller.Pin  # PA06
_C4: microcontroller.Pin  # PA23
_C3: microcontroller.Pin  # PA07
_C2: microcontroller.Pin  # PA14
_C1: microcontroller.Pin  # PA15
_BUTTONS: microcontroller.Pin  # PA08
P1: microcontroller.Pin  # PA30
P2: microcontroller.Pin  # PA31
P3: microcontroller.Pin  # PA00
P4: microcontroller.Pin  # PA01
P5: microcontroller.Pin  # PA02
P6: microcontroller.Pin  # PA03
P7: microcontroller.Pin  # PA04
SDA: microcontroller.Pin  # PA00
SCL: microcontroller.Pin  # PA01
TX: microcontroller.Pin  # PA00
RX: microcontroller.Pin  # PA01
MISO: microcontroller.Pin  # PA04
MOSI: microcontroller.Pin  # PA30
SCK: microcontroller.Pin  # PA31
DAC: microcontroller.Pin  # PA02


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
