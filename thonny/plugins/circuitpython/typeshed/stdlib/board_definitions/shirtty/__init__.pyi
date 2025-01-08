# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for @sarfata shIRtty
 - port: atmel-samd
 - board_id: shirtty
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
D0: microcontroller.Pin  # PA08
SDA: microcontroller.Pin  # PA08
D1: microcontroller.Pin  # PA10
IR_RX: microcontroller.Pin  # PA10
D2: microcontroller.Pin  # PA09
A2: microcontroller.Pin  # PA09
SCL: microcontroller.Pin  # PA09
MISO: microcontroller.Pin  # PA09
D3: microcontroller.Pin  # PA07
A3: microcontroller.Pin  # PA07
RX: microcontroller.Pin  # PA07
SCK: microcontroller.Pin  # PA07
D4: microcontroller.Pin  # PA06
A4: microcontroller.Pin  # PA06
TX: microcontroller.Pin  # PA06
MOSI: microcontroller.Pin  # PA06
D5: microcontroller.Pin  # PA14
D6: microcontroller.Pin  # PA15
D7: microcontroller.Pin  # PA16
D8: microcontroller.Pin  # PA23
IR_TX: microcontroller.Pin  # PA23


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
