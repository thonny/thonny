# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Arduino Nano 33 IoT
 - port: atmel-samd
 - board_id: arduino_nano_33_iot
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, os, pwmio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
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
A2: microcontroller.Pin  # PA11
A3: microcontroller.Pin  # PA10
A4: microcontroller.Pin  # PB08
SDA: microcontroller.Pin  # PB08
A5: microcontroller.Pin  # PB09
SCL: microcontroller.Pin  # PB09
A6: microcontroller.Pin  # PA09
A7: microcontroller.Pin  # PB03
D0: microcontroller.Pin  # PB23
RX: microcontroller.Pin  # PB23
D1: microcontroller.Pin  # PB22
TX: microcontroller.Pin  # PB22
D2: microcontroller.Pin  # PB10
D3: microcontroller.Pin  # PB11
D4: microcontroller.Pin  # PA07
D5: microcontroller.Pin  # PA05
D6: microcontroller.Pin  # PA04
D7: microcontroller.Pin  # PA06
D8: microcontroller.Pin  # PA18
D9: microcontroller.Pin  # PA20
D10: microcontroller.Pin  # PA21
D11: microcontroller.Pin  # PA16
MOSI: microcontroller.Pin  # PA16
D12: microcontroller.Pin  # PA19
MISO: microcontroller.Pin  # PA19
D13: microcontroller.Pin  # PA17
SCK: microcontroller.Pin  # PA17
LED: microcontroller.Pin  # PA17
ESP_RESET: microcontroller.Pin  # PA08
ESP_MOSI: microcontroller.Pin  # PA12
ESP_MISO: microcontroller.Pin  # PA13
ESP_CS: microcontroller.Pin  # PA14
ESP_SCK: microcontroller.Pin  # PA15
ESP_TX: microcontroller.Pin  # PA22
ESP_RX: microcontroller.Pin  # PA23
ESP_GPIO0: microcontroller.Pin  # PA27
ESP_BUSY: microcontroller.Pin  # PA28


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
