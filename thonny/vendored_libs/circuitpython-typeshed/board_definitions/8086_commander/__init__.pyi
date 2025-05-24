# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for 8086 Commander
 - port: atmel-samd
 - board_id: 8086_commander
 - NVM size: 256
 - Included modules: adafruit_bus_device, analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, math, microcontroller, neopixel_write, nvm, onewireio, os, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_hid, adafruit_sdcard
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # PA11
RX: microcontroller.Pin  # PA11
D1: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA10
D2: microcontroller.Pin  # PA20
B1: microcontroller.Pin  # PA20
D3: microcontroller.Pin  # PA09
B2: microcontroller.Pin  # PA09
D4: microcontroller.Pin  # PB09
B3: microcontroller.Pin  # PB09
D5: microcontroller.Pin  # PA02
B4: microcontroller.Pin  # PA02
D6: microcontroller.Pin  # PA13
CS: microcontroller.Pin  # PA13
D7: microcontroller.Pin  # PB10
MOSI: microcontroller.Pin  # PB10
D8: microcontroller.Pin  # PB11
SCK: microcontroller.Pin  # PB11
D9: microcontroller.Pin  # PA12
MISO: microcontroller.Pin  # PA12
D10: microcontroller.Pin  # PA15
LED1A: microcontroller.Pin  # PA15
D11: microcontroller.Pin  # PA14
LED1B: microcontroller.Pin  # PA14
D12: microcontroller.Pin  # PA08
LED2A: microcontroller.Pin  # PA08
D13: microcontroller.Pin  # PA07
LED2B: microcontroller.Pin  # PA07
D14: microcontroller.Pin  # PA06
ALERT: microcontroller.Pin  # PA06
D15: microcontroller.Pin  # PA05
LED3A: microcontroller.Pin  # PA05
D16: microcontroller.Pin  # PA04
LED3B: microcontroller.Pin  # PA04
D17: microcontroller.Pin  # PB02
LED4A: microcontroller.Pin  # PB02
D18: microcontroller.Pin  # PB03
LED4B: microcontroller.Pin  # PB03
D19: microcontroller.Pin  # PA23
SCL: microcontroller.Pin  # PA23
D20: microcontroller.Pin  # PA22
SDA: microcontroller.Pin  # PA22


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
