# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SAM E54 Xplained Pro
 - port: atmel-samd
 - board_id: same54_xplained
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
SDA: microcontroller.Pin  # PD08
SCL: microcontroller.Pin  # PD09
VSYNC: microcontroller.Pin  # PA12
HSYNC: microcontroller.Pin  # PA13
PCLK: microcontroller.Pin  # PA14
XCLK: microcontroller.Pin  # PA15
D07: microcontroller.Pin  # PA23
D06: microcontroller.Pin  # PA22
D05: microcontroller.Pin  # PA21
D04: microcontroller.Pin  # PA20
D03: microcontroller.Pin  # PA19
D02: microcontroller.Pin  # PA18
D01: microcontroller.Pin  # PA17
D00: microcontroller.Pin  # PA16
D09: microcontroller.Pin  # PB15
D08: microcontroller.Pin  # PB14
RST: microcontroller.Pin  # PC12
PWDN: microcontroller.Pin  # PC11
PDEC_A: microcontroller.Pin  # PC16
PDEC_B: microcontroller.Pin  # PC17
PDEC_C: microcontroller.Pin  # PC18
ADCDAC: microcontroller.Pin  # PA02
SW0: microcontroller.Pin  # PB31
LED: microcontroller.Pin  # PC18
QT: microcontroller.Pin  # PA16
CAN_RX: microcontroller.Pin  # PB13
CAN_TX: microcontroller.Pin  # PB12
CAN_STANDBY: microcontroller.Pin  # PC13
PB04: microcontroller.Pin  # PB04
PB05: microcontroller.Pin  # PB05
PA06: microcontroller.Pin  # PA06
PA07: microcontroller.Pin  # PA07
PB08: microcontroller.Pin  # PB08
PB09: microcontroller.Pin  # PB09
PB07: microcontroller.Pin  # PB07
PA27: microcontroller.Pin  # PA27
PC22: microcontroller.Pin  # PC22
PA23: microcontroller.Pin  # PA23
PA05: microcontroller.Pin  # PA05
PA04: microcontroller.Pin  # PA04
PB28: microcontroller.Pin  # PB28
PB27: microcontroller.Pin  # PB27
PB29: microcontroller.Pin  # PB29
PB26: microcontroller.Pin  # PB26
PB00: microcontroller.Pin  # PB00
PA03: microcontroller.Pin  # PA03
PB01: microcontroller.Pin  # PB01
PB06: microcontroller.Pin  # PB06
PB14: microcontroller.Pin  # PB14
PB15: microcontroller.Pin  # PB15
PD00: microcontroller.Pin  # PD00
PB02: microcontroller.Pin  # PB02
PD08: microcontroller.Pin  # PD08
PD09: microcontroller.Pin  # PD09
PB17: microcontroller.Pin  # PB17
PB16: microcontroller.Pin  # PB16
PC06: microcontroller.Pin  # PC06
PC04: microcontroller.Pin  # PC04
PC07: microcontroller.Pin  # PC07
PC05: microcontroller.Pin  # PC05
PC02: microcontroller.Pin  # PC02
PC03: microcontroller.Pin  # PC03
PC10: microcontroller.Pin  # PC10
PC01: microcontroller.Pin  # PC01
PD11: microcontroller.Pin  # PD11
PD10: microcontroller.Pin  # PD10
PC31: microcontroller.Pin  # PC31
PC30: microcontroller.Pin  # PC30
PD09: microcontroller.Pin  # PD09
PD08: microcontroller.Pin  # PD08
PC22: microcontroller.Pin  # PC22
PC23: microcontroller.Pin  # PC23
PC04: microcontroller.Pin  # PC04
PC14: microcontroller.Pin  # PC14
PC05: microcontroller.Pin  # PC05
PC07: microcontroller.Pin  # PC07
SDIO_CLOCK: microcontroller.Pin  # PA21
SDIO_COMMAND: microcontroller.Pin  # PA20


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

SDIO_DATA: Tuple[Any]


# Unmapped:
#   none
