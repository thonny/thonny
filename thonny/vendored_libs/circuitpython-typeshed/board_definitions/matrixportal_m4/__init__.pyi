# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Matrix Portal M4
 - port: atmel-samd
 - board_id: matrixportal_m4
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_esp32spi, adafruit_portalbase, adafruit_requests, neopixel
"""

# Imports
import busio
import microcontroller
from typing import Any, Dict, Tuple


# Board Info:
board_id: str


# Pins:
clock_pin: microcontroller.Pin  # PB06
latch_pin: microcontroller.Pin  # PB14
output_enable_pin: microcontroller.Pin  # PB12
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA04
A3: microcontroller.Pin  # PA06
A4: microcontroller.Pin  # PA07
TX: microcontroller.Pin  # PA00
RX: microcontroller.Pin  # PA01
ESP_CS: microcontroller.Pin  # PB17
ESP_GPIO0: microcontroller.Pin  # PA20
ESP_BUSY: microcontroller.Pin  # PA22
ESP_RESET: microcontroller.Pin  # PA21
ESP_RTS: microcontroller.Pin  # PA18
ESP_TX: microcontroller.Pin  # PA13
ESP_RX: microcontroller.Pin  # PA12
SCL: microcontroller.Pin  # PB30
SDA: microcontroller.Pin  # PB31
NEOPIXEL: microcontroller.Pin  # PA23
SCK: microcontroller.Pin  # PA16
MOSI: microcontroller.Pin  # PA19
MISO: microcontroller.Pin  # PA17
MTX_R1: microcontroller.Pin  # PB00
MTX_G1: microcontroller.Pin  # PB01
MTX_B1: microcontroller.Pin  # PB02
MTX_R2: microcontroller.Pin  # PB03
MTX_G2: microcontroller.Pin  # PB04
MTX_B2: microcontroller.Pin  # PB05
MTX_ADDRA: microcontroller.Pin  # PB07
MTX_ADDRB: microcontroller.Pin  # PB08
MTX_ADDRC: microcontroller.Pin  # PB09
MTX_ADDRD: microcontroller.Pin  # PB15
MTX_ADDRE: microcontroller.Pin  # PB13
MTX_CLK: microcontroller.Pin  # PB06
MTX_LAT: microcontroller.Pin  # PB14
MTX_OE: microcontroller.Pin  # PB12
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # PA27
BUTTON_UP: microcontroller.Pin  # PB22
BUTTON_DOWN: microcontroller.Pin  # PB23
LED: microcontroller.Pin  # PA14
L: microcontroller.Pin  # PA14


# Members:
rgb_pins: Tuple[Any]

MTX_ADDRESS: Tuple[Any]

MTX_COMMON: Dict[str, Any]

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
