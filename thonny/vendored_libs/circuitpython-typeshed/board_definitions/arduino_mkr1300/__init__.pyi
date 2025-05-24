# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Arduino MKR1300
 - port: atmel-samd
 - board_id: arduino_mkr1300
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pwmio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PB02
A2: microcontroller.Pin  # PB03
A3: microcontroller.Pin  # PA04
A4: microcontroller.Pin  # PA05
A5: microcontroller.Pin  # PA06
A6: microcontroller.Pin  # PA07
D0: microcontroller.Pin  # PA22
RX: microcontroller.Pin  # PB23
D1: microcontroller.Pin  # PA23
TX: microcontroller.Pin  # PB22
D2: microcontroller.Pin  # PA10
D3: microcontroller.Pin  # PA11
D4: microcontroller.Pin  # PB10
D5: microcontroller.Pin  # PB11
D6: microcontroller.Pin  # PA20
LED: microcontroller.Pin  # PA20
D7: microcontroller.Pin  # PA21
D8: microcontroller.Pin  # PA16
D9: microcontroller.Pin  # PA17
D10: microcontroller.Pin  # PA19
D11: microcontroller.Pin  # PA08
D12: microcontroller.Pin  # PA09
D13: microcontroller.Pin  # PB23
D14: microcontroller.Pin  # PB22
BOOT: microcontroller.Pin  # PB09
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09
SCK: microcontroller.Pin  # PA13
MOSI: microcontroller.Pin  # PA12
MISO: microcontroller.Pin  # PA15
RFM9X_RST: microcontroller.Pin  # PA27
RFM9X_CS: microcontroller.Pin  # PA14
VOLTAGE_MONITOR: microcontroller.Pin  # PB08
BATTERY: microcontroller.Pin  # PB08


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
