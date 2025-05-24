# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun Qwiic Micro
 - port: atmel-samd
 - board_id: sparkfun_qwiic_micro_no_flash
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
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA06
A2: microcontroller.Pin  # PA05
A3: microcontroller.Pin  # PA07
A4: microcontroller.Pin  # PA10
A5: microcontroller.Pin  # PA04
D0: microcontroller.Pin  # PA08
D1: microcontroller.Pin  # PA02
D2: microcontroller.Pin  # PA06
D3: microcontroller.Pin  # PA05
D4: microcontroller.Pin  # PA07
D5: microcontroller.Pin  # PA00
D6: microcontroller.Pin  # PA01
D7: microcontroller.Pin  # PA04
D8: microcontroller.Pin  # PA09
D13: microcontroller.Pin  # PA10
LED: microcontroller.Pin  # PA10
D16: microcontroller.Pin  # PA22
D17: microcontroller.Pin  # PA23
SCK: microcontroller.Pin  # PA07
MOSI: microcontroller.Pin  # PA06
MISO: microcontroller.Pin  # PA05
TX: microcontroller.Pin  # PA22
RX: microcontroller.Pin  # PA23
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
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
