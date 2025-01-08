# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Meow Meow
 - port: atmel-samd
 - board_id: meowmeow
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
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
A2: microcontroller.Pin  # PA04
A3: microcontroller.Pin  # PA05
A4: microcontroller.Pin  # PA06
A5: microcontroller.Pin  # PA07
A6: microcontroller.Pin  # PB02
A7: microcontroller.Pin  # PB03
A8: microcontroller.Pin  # PB08
A9: microcontroller.Pin  # PB09
A10: microcontroller.Pin  # PA11
A11: microcontroller.Pin  # PA09
D0: microcontroller.Pin  # PA11
RX: microcontroller.Pin  # PA11
D1: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA10
D2: microcontroller.Pin  # PB02
D3: microcontroller.Pin  # PB03
D4: microcontroller.Pin  # PA14
D5: microcontroller.Pin  # PA05
D6: microcontroller.Pin  # PA15
D7: microcontroller.Pin  # PB22
D8: microcontroller.Pin  # PA06
D9: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA30
D11: microcontroller.Pin  # PA31
D12: microcontroller.Pin  # PA02
D13: microcontroller.Pin  # PB23
LED: microcontroller.Pin  # PB23
SDA: microcontroller.Pin  # PA00
SCL: microcontroller.Pin  # PA01
SCK: microcontroller.Pin  # PA15
MOSI: microcontroller.Pin  # PA14
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
