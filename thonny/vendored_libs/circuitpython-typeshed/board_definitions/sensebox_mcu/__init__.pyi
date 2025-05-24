# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for senseBox MCU
 - port: atmel-samd
 - board_id: sensebox_mcu
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A1: microcontroller.Pin  # PA04
A2: microcontroller.Pin  # PA05
A3: microcontroller.Pin  # PA06
A4: microcontroller.Pin  # PA07
A5: microcontroller.Pin  # PA03
A6: microcontroller.Pin  # PA02
D1: microcontroller.Pin  # PA04
D2: microcontroller.Pin  # PA05
D3: microcontroller.Pin  # PA06
D4: microcontroller.Pin  # PA07
D5: microcontroller.Pin  # PA03
D6: microcontroller.Pin  # PA02
D7: microcontroller.Pin  # PA27
D8: microcontroller.Pin  # PA28
D9: microcontroller.Pin  # PB02
D10: microcontroller.Pin  # PA22
D11: microcontroller.Pin  # PA23
D12: microcontroller.Pin  # PB08
D13: microcontroller.Pin  # PB09
UART_PWR: microcontroller.Pin  # PB02
TX1: microcontroller.Pin  # PA22
RX1: microcontroller.Pin  # PA23
TX2: microcontroller.Pin  # PB08
RX2: microcontroller.Pin  # PB09
TX: microcontroller.Pin  # PA22
RX: microcontroller.Pin  # PA23
MOSI: microcontroller.Pin  # PA16
SCK: microcontroller.Pin  # PA17
MISO: microcontroller.Pin  # PA19
I2C_PWR: microcontroller.Pin  # PB11
SCL: microcontroller.Pin  # PA09
SDA: microcontroller.Pin  # PA08
LED: microcontroller.Pin  # PA27
RED_LED: microcontroller.Pin  # PA27
GREEN_LED: microcontroller.Pin  # PA28
XB1_PWR: microcontroller.Pin  # PB03
XB2_PWR: microcontroller.Pin  # PB10
XB1_CS: microcontroller.Pin  # PA18
XB2_CS: microcontroller.Pin  # PA14
XB1_INT: microcontroller.Pin  # PA21
XB2_INT: microcontroller.Pin  # PA15
XB1_RX: microcontroller.Pin  # PA23
XB1_TX: microcontroller.Pin  # PA22
XB2_RX: microcontroller.Pin  # PA11
XB2_TX: microcontroller.Pin  # PA10


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
