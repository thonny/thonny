# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Electronic Cats CatWAN USBStick
 - port: atmel-samd
 - board_id: catwan_usbstick
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
D0: microcontroller.Pin  # PA30
D1: microcontroller.Pin  # PA31
RFM9X_D0: microcontroller.Pin  # PA04
RFM9X_D1: microcontroller.Pin  # PA23
RFM9X_D2: microcontroller.Pin  # PA27
RFM9X_D5: microcontroller.Pin  # PA15
RFM9X_RST: microcontroller.Pin  # PA16
RFM9X_CS: microcontroller.Pin  # PA17
LED: microcontroller.Pin  # PA14
SCK: microcontroller.Pin  # PA19
MOSI: microcontroller.Pin  # PA18
MISO: microcontroller.Pin  # PA22


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
