# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Escornabot Makech
 - port: atmel-samd
 - board_id: escornabot_makech
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
A0: microcontroller.Pin  # PA02
LED: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA04
A2: microcontroller.Pin  # PA05
A3: microcontroller.Pin  # PA10
A4: microcontroller.Pin  # PA03
D0: microcontroller.Pin  # PA00
D1: microcontroller.Pin  # PA01
D2: microcontroller.Pin  # PA22
D3: microcontroller.Pin  # PA11
D4: microcontroller.Pin  # PA27
D5: microcontroller.Pin  # PA28
D6: microcontroller.Pin  # PA06
D7: microcontroller.Pin  # PA07
D8: microcontroller.Pin  # PA18
D9: microcontroller.Pin  # PA17
D10: microcontroller.Pin  # PA16
D11: microcontroller.Pin  # PA08
D12: microcontroller.Pin  # PA09
D13: microcontroller.Pin  # PA13
RX: microcontroller.Pin  # PA01
TX: microcontroller.Pin  # PA00
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09
SCK: microcontroller.Pin  # PA15
MOSI: microcontroller.Pin  # PA12
MISO: microcontroller.Pin  # PA13
ESP_CS: microcontroller.Pin  # PA14
ESP_GPIO0: microcontroller.Pin  # PA20
ESP_BUSY: microcontroller.Pin  # PA21
ESP_RESET: microcontroller.Pin  # PA23
ESP_RTS: microcontroller.Pin  # PA19


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
