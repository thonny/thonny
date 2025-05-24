# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather M0 Express with Crickit libraries
 - port: atmel-samd
 - board_id: feather_m0_express_crickit
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busio, busio.SPI, busio.UART, codeop, collections, digitalio, errno, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: adafruit_crickit, adafruit_motor, adafruit_seesaw, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PB08
A2: microcontroller.Pin  # PB09
A3: microcontroller.Pin  # PA04
A4: microcontroller.Pin  # PA05
A5: microcontroller.Pin  # PB02
SCK: microcontroller.Pin  # PB11
MOSI: microcontroller.Pin  # PB10
MISO: microcontroller.Pin  # PA12
D0: microcontroller.Pin  # PA11
RX: microcontroller.Pin  # PA11
D1: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA10
SDA: microcontroller.Pin  # PA22
SCL: microcontroller.Pin  # PA23
D5: microcontroller.Pin  # PA15
D6: microcontroller.Pin  # PA20
D9: microcontroller.Pin  # PA07
VOLTAGE_MONITOR: microcontroller.Pin  # PA07
BATTERY: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA18
D11: microcontroller.Pin  # PA16
D12: microcontroller.Pin  # PA19
LED: microcontroller.Pin  # PA17
D13: microcontroller.Pin  # PA17
NEOPIXEL: microcontroller.Pin  # PA06


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
