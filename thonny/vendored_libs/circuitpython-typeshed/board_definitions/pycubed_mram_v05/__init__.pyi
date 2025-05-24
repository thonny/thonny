# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PyCubedv05-MRAM
 - port: atmel-samd
 - board_id: pycubed_mram_v05
 - NVM size: 256
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, board, builtins, builtins.pow3, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, errno, floppyio, frequencyio, getpass, i2ctarget, io, json, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, synthio, sys, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, warnings, watchdog, zlib
 - Frozen libraries: adafruit_register, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SCK: microcontroller.Pin  # PA13
MOSI: microcontroller.Pin  # PA12
MISO: microcontroller.Pin  # PA14
SD_CS: microcontroller.Pin  # PA27
RELAY_A: microcontroller.Pin  # PB15
BURN1: microcontroller.Pin  # PB31
BURN2: microcontroller.Pin  # PA15
DAC0: microcontroller.Pin  # PA02
EN_RF: microcontroller.Pin  # PA04
AIN5: microcontroller.Pin  # PA05
BATTERY: microcontroller.Pin  # PA06
L1PROG: microcontroller.Pin  # PA07
CHRG: microcontroller.Pin  # PB08
PA16: microcontroller.Pin  # PA16
PA17: microcontroller.Pin  # PA17
VBUS_RST: microcontroller.Pin  # PA18
PA19: microcontroller.Pin  # PA19
PA20: microcontroller.Pin  # PA20
PA22: microcontroller.Pin  # PA22
PB16: microcontroller.Pin  # PB16
PB17: microcontroller.Pin  # PB17
PB22: microcontroller.Pin  # PB22
PB23: microcontroller.Pin  # PB23
RF1_RST: microcontroller.Pin  # PB00
RF1_CS: microcontroller.Pin  # PB30
RF1_IO4: microcontroller.Pin  # PB04
RF1_IO0: microcontroller.Pin  # PB05
RF2_IO0: microcontroller.Pin  # PB06
RF2_IO4: microcontroller.Pin  # PB07
RF2_CS: microcontroller.Pin  # PB09
RF2_RST: microcontroller.Pin  # PB14
EN_GPS: microcontroller.Pin  # PB01
TX: microcontroller.Pin  # PB02
RX: microcontroller.Pin  # PB03
TX2: microcontroller.Pin  # PA17
RX2: microcontroller.Pin  # PA16
SDA: microcontroller.Pin  # PB12
SCL: microcontroller.Pin  # PB13
SCL2: microcontroller.Pin  # PA16
SDA2: microcontroller.Pin  # PA17
WDT_WDI: microcontroller.Pin  # PA23
NEOPIXEL: microcontroller.Pin  # PA21


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
