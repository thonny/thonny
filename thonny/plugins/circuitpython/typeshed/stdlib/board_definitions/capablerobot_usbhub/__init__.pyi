# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Capable Robot Programmable USB Hub
 - port: atmel-samd
 - board_id: capablerobot_usbhub
 - NVM size: 256
 - Included modules: alarm, analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, nvm, onewireio, os, ps2io, pwmio, rainbowio, random, rtc, samd, storage, struct, supervisor, sys, time, usb_cdc, watchdog
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
ANMB: microcontroller.Pin  # PA02
ANVLIM: microcontroller.Pin  # PA04
AN5V: microcontroller.Pin  # PA05
MBPWM: microcontroller.Pin  # PA14
MBINT: microcontroller.Pin  # PA15
MBCS: microcontroller.Pin  # PA18
MBRST: microcontroller.Pin  # PB09
LED1: microcontroller.Pin  # PA19
LED2: microcontroller.Pin  # PA20
LED3: microcontroller.Pin  # PA21
RX: microcontroller.Pin  # PA16
TX: microcontroller.Pin  # PA17
USBHOSTEN: microcontroller.Pin  # PA07
USBRESET: microcontroller.Pin  # PB08
USBBCEN: microcontroller.Pin  # PB22
PCBREV: microcontroller.Pin  # PB02
SDA: microcontroller.Pin  # PA22
SCL: microcontroller.Pin  # PA23
SDA2: microcontroller.Pin  # PA12
SCL2: microcontroller.Pin  # PA13
SCK: microcontroller.Pin  # PA01
MOSI: microcontroller.Pin  # PA00
MISO: microcontroller.Pin  # PB23


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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
