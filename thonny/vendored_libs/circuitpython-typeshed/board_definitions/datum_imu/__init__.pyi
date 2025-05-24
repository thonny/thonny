# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for J&J Studios datum-IMU
 - port: atmel-samd
 - board_id: datum_imu
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
A1: microcontroller.Pin  # PA03
SCK: microcontroller.Pin  # PB11
MOSI: microcontroller.Pin  # PB10
MISO: microcontroller.Pin  # PA12
D0: microcontroller.Pin  # PA11
RX: microcontroller.Pin  # PA11
D1: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA10
SDA: microcontroller.Pin  # PA22
SCL: microcontroller.Pin  # PA23
D3: microcontroller.Pin  # PA09
D4: microcontroller.Pin  # PA08
D6: microcontroller.Pin  # PA20
D7: microcontroller.Pin  # PA21
D8: microcontroller.Pin  # PA06
D9: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA18
D11: microcontroller.Pin  # PA16
D12: microcontroller.Pin  # PA19
D13: microcontroller.Pin  # PA17
LED: microcontroller.Pin  # PA17
TX_LED: microcontroller.Pin  # PA27


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
