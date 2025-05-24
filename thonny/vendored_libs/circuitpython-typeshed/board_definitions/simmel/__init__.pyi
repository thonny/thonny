# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Simmel
 - port: nordic
 - board_id: simmel
 - NVM size: 8192
 - Included modules: _bleio, aesio, analogio, array, audiobusio, audiocore, audiopwmio, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, os, pwmio, random, rtc, storage, struct, supervisor, sys, time, usb_hid, watchdog
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SPI_CSN: microcontroller.Pin  # P1_06
SPI_MISO: microcontroller.Pin  # P1_04
SPI_MOSI: microcontroller.Pin  # P0_09
SPI_SCK: microcontroller.Pin  # P0_10
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
LED: microcontroller.Pin  # P0_06
SCL: microcontroller.Pin  # P0_08
SDA: microcontroller.Pin  # P1_09


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
