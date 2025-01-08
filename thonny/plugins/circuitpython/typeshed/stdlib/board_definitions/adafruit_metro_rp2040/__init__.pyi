# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Metro RP2040
 - port: raspberrypi
 - board_id: adafruit_metro_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
D24: microcontroller.Pin  # GPIO24
D25: microcontroller.Pin  # GPIO25
D0: microcontroller.Pin  # GPIO0
RX_D0_SWITCH_LEFT: microcontroller.Pin  # GPIO0
TX_D0_SWITCH_RIGHT: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
TX_D1_SWITCH_LEFT: microcontroller.Pin  # GPIO1
RX_D1_SWITCH_RIGHT: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO8
D9: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
D12: microcontroller.Pin  # GPIO12
LED: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO17
NEOPIXEL: microcontroller.Pin  # GPIO14
SD_CD: microcontroller.Pin  # GPIO15
SCK: microcontroller.Pin  # GPIO18
SDIO_CLOCK: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO19
SDIO_COMMAND: microcontroller.Pin  # GPIO19
MISO: microcontroller.Pin  # GPIO20
SDIO_DATA0: microcontroller.Pin  # GPIO20
SDIO_DATA1: microcontroller.Pin  # GPIO21
SDIO_DATA2: microcontroller.Pin  # GPIO22
SD_CS: microcontroller.Pin  # GPIO23
SDIO_DATA3: microcontroller.Pin  # GPIO23


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
