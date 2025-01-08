# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Grand Central M4 Express
 - port: atmel-samd
 - board_id: grandcentral_m4_express
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
AREF: microcontroller.Pin  # PA03
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PB03
A3: microcontroller.Pin  # PC00
A4: microcontroller.Pin  # PC01
A5: microcontroller.Pin  # PC02
A6: microcontroller.Pin  # PC03
A7: microcontroller.Pin  # PB04
A8: microcontroller.Pin  # PB05
A9: microcontroller.Pin  # PB06
A10: microcontroller.Pin  # PB07
A11: microcontroller.Pin  # PB08
A12: microcontroller.Pin  # PB09
A13: microcontroller.Pin  # PA04
A14: microcontroller.Pin  # PA06
A15: microcontroller.Pin  # PA07
D0: microcontroller.Pin  # PB25
RX: microcontroller.Pin  # PB25
D1: microcontroller.Pin  # PB24
TX: microcontroller.Pin  # PB24
D2: microcontroller.Pin  # PC18
D3: microcontroller.Pin  # PC19
D4: microcontroller.Pin  # PC20
D5: microcontroller.Pin  # PC21
D6: microcontroller.Pin  # PD20
D7: microcontroller.Pin  # PD21
D8: microcontroller.Pin  # PB18
D9: microcontroller.Pin  # PB02
D10: microcontroller.Pin  # PB22
D11: microcontroller.Pin  # PB23
D12: microcontroller.Pin  # PB00
LED: microcontroller.Pin  # PB01
D13: microcontroller.Pin  # PB01
D14: microcontroller.Pin  # PB16
TX3: microcontroller.Pin  # PB16
D15: microcontroller.Pin  # PB17
RX3: microcontroller.Pin  # PB17
D16: microcontroller.Pin  # PC22
TX2: microcontroller.Pin  # PC22
D17: microcontroller.Pin  # PC23
RX2: microcontroller.Pin  # PC23
D18: microcontroller.Pin  # PB12
TX1: microcontroller.Pin  # PB12
D19: microcontroller.Pin  # PB13
RX1: microcontroller.Pin  # PB13
D20: microcontroller.Pin  # PB20
SDA: microcontroller.Pin  # PB20
D21: microcontroller.Pin  # PB21
SCL: microcontroller.Pin  # PB21
D22: microcontroller.Pin  # PD12
D23: microcontroller.Pin  # PA15
D24: microcontroller.Pin  # PC17
SCL1: microcontroller.Pin  # PC17
D25: microcontroller.Pin  # PC16
SDA1: microcontroller.Pin  # PC16
D26: microcontroller.Pin  # PA12
PCC_DEN1: microcontroller.Pin  # PA12
D27: microcontroller.Pin  # PA13
PCC_DEN2: microcontroller.Pin  # PA13
D28: microcontroller.Pin  # PA14
PCC_CLK: microcontroller.Pin  # PA14
D29: microcontroller.Pin  # PB19
PCC_XCLK: microcontroller.Pin  # PB19
D30: microcontroller.Pin  # PA23
PCC_D7: microcontroller.Pin  # PA23
D31: microcontroller.Pin  # PA22
PCC_D6: microcontroller.Pin  # PA22
D32: microcontroller.Pin  # PA21
PCC_D5: microcontroller.Pin  # PA21
D33: microcontroller.Pin  # PA20
PCC_D4: microcontroller.Pin  # PA20
D34: microcontroller.Pin  # PA19
PCC_D3: microcontroller.Pin  # PA19
D35: microcontroller.Pin  # PA18
PCC_D2: microcontroller.Pin  # PA18
D36: microcontroller.Pin  # PA17
PCC_D1: microcontroller.Pin  # PA17
D37: microcontroller.Pin  # PA16
PCC_D0: microcontroller.Pin  # PA16
D38: microcontroller.Pin  # PB15
PCC_D9: microcontroller.Pin  # PB15
D39: microcontroller.Pin  # PB14
PCC_D8: microcontroller.Pin  # PB14
D40: microcontroller.Pin  # PC13
PCC_D11: microcontroller.Pin  # PC13
D41: microcontroller.Pin  # PC12
PCC_D10: microcontroller.Pin  # PC12
D42: microcontroller.Pin  # PC15
PCC_D13: microcontroller.Pin  # PC15
D43: microcontroller.Pin  # PC14
PCC_D12: microcontroller.Pin  # PC14
D44: microcontroller.Pin  # PC11
D45: microcontroller.Pin  # PC10
D46: microcontroller.Pin  # PC06
D47: microcontroller.Pin  # PC07
D48: microcontroller.Pin  # PC04
D49: microcontroller.Pin  # PC05
D50: microcontroller.Pin  # PD11
MISO: microcontroller.Pin  # PD11
D51: microcontroller.Pin  # PD08
MOSI: microcontroller.Pin  # PD08
D52: microcontroller.Pin  # PD09
SCK: microcontroller.Pin  # PD09
D53: microcontroller.Pin  # PD10
SS: microcontroller.Pin  # PD10
SD_MOSI: microcontroller.Pin  # PB26
SD_SCK: microcontroller.Pin  # PB27
SD_CS: microcontroller.Pin  # PB28
SD_MISO: microcontroller.Pin  # PB29
SD_CARD_DETECT: microcontroller.Pin  # PB31
NEOPIXEL: microcontroller.Pin  # PC24
LED_RX: microcontroller.Pin  # PC31
LED_TX: microcontroller.Pin  # PC30
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
