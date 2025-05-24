# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for P1AM-200
 - port: atmel-samd
 - board_id: p1am_200
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, spitarget, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
AREF: microcontroller.Pin  # PA03
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PB00
A3: microcontroller.Pin  # PC00
A4: microcontroller.Pin  # PC01
A5: microcontroller.Pin  # PC02
A6: microcontroller.Pin  # PC03
DE1: microcontroller.Pin  # PC03
D0: microcontroller.Pin  # PA23
TX2: microcontroller.Pin  # PA23
D1: microcontroller.Pin  # PA22
RX2: microcontroller.Pin  # PA22
D2: microcontroller.Pin  # PC18
SERIAL_MODE2: microcontroller.Pin  # PC18
D3: microcontroller.Pin  # PC19
SERIAL_MODE1: microcontroller.Pin  # PC19
D4: microcontroller.Pin  # PC20
D5: microcontroller.Pin  # PC10
D6: microcontroller.Pin  # PA12
DE2: microcontroller.Pin  # PA12
D7: microcontroller.Pin  # PA13
D8: microcontroller.Pin  # PD08
MOSI: microcontroller.Pin  # PD08
D9: microcontroller.Pin  # PD09
SCK: microcontroller.Pin  # PD09
D10: microcontroller.Pin  # PD11
MISO: microcontroller.Pin  # PD11
D11: microcontroller.Pin  # PB20
SDA: microcontroller.Pin  # PB20
D12: microcontroller.Pin  # PB21
SCL: microcontroller.Pin  # PB21
D13: microcontroller.Pin  # PB13
RX1: microcontroller.Pin  # PB13
D14: microcontroller.Pin  # PB12
TX1: microcontroller.Pin  # PB12
LED: microcontroller.Pin  # PB01
SWITCH: microcontroller.Pin  # PB02
NEOPIXEL: microcontroller.Pin  # PC24
BC_MOSI: microcontroller.Pin  # PC22
BC_SCK: microcontroller.Pin  # PC23
BC_CS: microcontroller.Pin  # PD20
BC_MISO: microcontroller.Pin  # PD21
BC_READY: microcontroller.Pin  # PB16
BC_EN: microcontroller.Pin  # PB17
ATMAC_SDA: microcontroller.Pin  # PC16
ATMAC_SCL: microcontroller.Pin  # PC17
RTC_SDA: microcontroller.Pin  # PC16
RTC_SCL: microcontroller.Pin  # PC17
P24V: microcontroller.Pin  # PC31
SD_MOSI: microcontroller.Pin  # PB26
SD_SCK: microcontroller.Pin  # PB27
SD_CS: microcontroller.Pin  # PB28
SD_MISO: microcontroller.Pin  # PB29
SD_CARD_DETECT: microcontroller.Pin  # PB31


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
