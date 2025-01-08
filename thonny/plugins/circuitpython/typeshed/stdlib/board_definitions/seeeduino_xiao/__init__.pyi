# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Seeeduino XIAO
 - port: atmel-samd
 - board_id: seeeduino_xiao
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
A1: microcontroller.Pin  # PA04
A2: microcontroller.Pin  # PA10
A3: microcontroller.Pin  # PA11
A4: microcontroller.Pin  # PA08
A5: microcontroller.Pin  # PA09
A6: microcontroller.Pin  # PB08
A7: microcontroller.Pin  # PB09
A8: microcontroller.Pin  # PA07
A9: microcontroller.Pin  # PA05
A10: microcontroller.Pin  # PA06
D0: microcontroller.Pin  # PA02
D1: microcontroller.Pin  # PA04
D2: microcontroller.Pin  # PA10
D3: microcontroller.Pin  # PA11
D4: microcontroller.Pin  # PA08
D5: microcontroller.Pin  # PA09
D6: microcontroller.Pin  # PB08
D7: microcontroller.Pin  # PB09
D8: microcontroller.Pin  # PA07
D9: microcontroller.Pin  # PA05
D10: microcontroller.Pin  # PA06
TX: microcontroller.Pin  # PB08
RX: microcontroller.Pin  # PB09
MOSI: microcontroller.Pin  # PA06
SCK: microcontroller.Pin  # PA07
MISO: microcontroller.Pin  # PA05
SCL: microcontroller.Pin  # PA09
SDA: microcontroller.Pin  # PA08
LED_INVERTED: microcontroller.Pin  # PA17
YELLOW_LED_INVERTED: microcontroller.Pin  # PA17
RX_LED_INVERTED: microcontroller.Pin  # PA18
BLUE_LED1_INVERTED: microcontroller.Pin  # PA18
TX_LED_INVERTED: microcontroller.Pin  # PA19
BLUE_LED2_INVERTED: microcontroller.Pin  # PA19


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
