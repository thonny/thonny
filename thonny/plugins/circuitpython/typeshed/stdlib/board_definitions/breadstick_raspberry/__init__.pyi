# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Raspberry Breadstick
 - port: raspberrypi
 - board_id: breadstick_raspberry
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_dotstar, adafruit_lsm6ds, adafruit_register
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D1_A1: microcontroller.Pin  # GPIO27
D1: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
D2_A2: microcontroller.Pin  # GPIO26
D2: microcontroller.Pin  # GPIO26
A2: microcontroller.Pin  # GPIO26
D3: microcontroller.Pin  # GPIO11
D4: microcontroller.Pin  # GPIO10
D5: microcontroller.Pin  # GPIO9
D6: microcontroller.Pin  # GPIO8
D7: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO6
D9: microcontroller.Pin  # GPIO5
D10: microcontroller.Pin  # GPIO24
D11: microcontroller.Pin  # GPIO23
D12: microcontroller.Pin  # GPIO22
D13: microcontroller.Pin  # GPIO21
D14: microcontroller.Pin  # GPIO20
D15: microcontroller.Pin  # GPIO19
D16: microcontroller.Pin  # GPIO18
D17_A17: microcontroller.Pin  # GPIO29
D17: microcontroller.Pin  # GPIO29
A17: microcontroller.Pin  # GPIO29
D18_A18: microcontroller.Pin  # GPIO28
D18: microcontroller.Pin  # GPIO28
A18: microcontroller.Pin  # GPIO28
APA102_MOSI: microcontroller.Pin  # GPIO17
DOTSTAR_DATA: microcontroller.Pin  # GPIO17
APA102_SCK: microcontroller.Pin  # GPIO16
DOTSTAR_CLOCK: microcontroller.Pin  # GPIO16
IMU_SDA: microcontroller.Pin  # GPIO12
IMU_SCL: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO22
SCL: microcontroller.Pin  # GPIO23
MOSI: microcontroller.Pin  # GPIO11
SCK: microcontroller.Pin  # GPIO10
CS: microcontroller.Pin  # GPIO9
MISO: microcontroller.Pin  # GPIO8
RX: microcontroller.Pin  # GPIO21
TX: microcontroller.Pin  # GPIO20


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
