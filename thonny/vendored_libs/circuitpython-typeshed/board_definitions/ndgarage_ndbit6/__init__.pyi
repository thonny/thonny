# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ndGarage[n°]Bit6:FeatherSnow
 - port: atmel-samd
 - board_id: ndgarage_ndbit6
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
D1: microcontroller.Pin  # PA05
D2: microcontroller.Pin  # PA08
D3: microcontroller.Pin  # PA11
D4: microcontroller.Pin  # PA22
D5: microcontroller.Pin  # PA28
D6: microcontroller.Pin  # PA00
D7: microcontroller.Pin  # PA03
D8: microcontroller.Pin  # PA06
D9: microcontroller.Pin  # PA09
D10: microcontroller.Pin  # PA15
D11: microcontroller.Pin  # PA23
D12: microcontroller.Pin  # PA01
D13: microcontroller.Pin  # PA04
D14: microcontroller.Pin  # PA07
D15: microcontroller.Pin  # PA10
D16: microcontroller.Pin  # PA14
D17: microcontroller.Pin  # PA27
D18: microcontroller.Pin  # PA02
MOSI: microcontroller.Pin  # PA04
MISO: microcontroller.Pin  # PA06
SCK: microcontroller.Pin  # PA05
TX: microcontroller.Pin  # PA08
RX: microcontroller.Pin  # PA09
SCL: microcontroller.Pin  # PA09
SDA: microcontroller.Pin  # PA08
L: microcontroller.Pin  # PA23
LED: microcontroller.Pin  # PA23


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
