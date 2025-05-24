# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for DynaLoRa_USB
 - port: atmel-samd
 - board_id: dynalora_usb
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, onewireio, os, pwmio, rainbowio, random, rotaryio, rtc, sdcardio, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_rfm9x, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # PA00
D1: microcontroller.Pin  # PA01
D2: microcontroller.Pin  # PA02
D3: microcontroller.Pin  # PA30
D4: microcontroller.Pin  # PA31
A0: microcontroller.Pin  # PA00
A1: microcontroller.Pin  # PA01
A2: microcontroller.Pin  # PA02
MOSI: microcontroller.Pin  # PA16
MISO: microcontroller.Pin  # PA18
SCK: microcontroller.Pin  # PA17
RADIO_CS: microcontroller.Pin  # PA11
RADIO_INT: microcontroller.Pin  # PA09
RADIO_RESET: microcontroller.Pin  # PA10
SD_CS: microcontroller.Pin  # PA03
SCL: microcontroller.Pin  # PA01
SDA: microcontroller.Pin  # PA00
RX: microcontroller.Pin  # PA01
TX: microcontroller.Pin  # PA00
MOSI1: microcontroller.Pin  # PA00
MISO1: microcontroller.Pin  # PA02
SCK1: microcontroller.Pin  # PA01
LED: microcontroller.Pin  # PA27
NEOPIXEL: microcontroller.Pin  # PA19
BUTTON: microcontroller.Pin  # PA15


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
