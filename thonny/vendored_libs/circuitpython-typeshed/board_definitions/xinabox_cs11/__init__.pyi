# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for XinaBox CS11
 - port: atmel-samd
 - board_id: xinabox_cs11
 - NVM size: 256
 - Included modules: adafruit_bus_device, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, nvm, os, pwmio, rainbowio, random, sdcardio, storage, struct, supervisor, sys, time, usb_cdc, usb_hid
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
RX: microcontroller.Pin  # PA11
TX: microcontroller.Pin  # PA10
CS: microcontroller.Pin  # PA09
ALERT: microcontroller.Pin  # PA07
RED: microcontroller.Pin  # PA16
GREEN: microcontroller.Pin  # PA19
BLUE: microcontroller.Pin  # PA17
SDA: microcontroller.Pin  # PA22
SCL: microcontroller.Pin  # PA23
SCK: microcontroller.Pin  # PB11
MOSI: microcontroller.Pin  # PB10
MISO: microcontroller.Pin  # PA12


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
