# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Maple Computing Elite-Pi
 - port: raspberrypi
 - board_id: maple_elite_pi
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
D0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
TX0: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
RX0: microcontroller.Pin  # GPIO1
D10_GND: microcontroller.Pin  # GPIO10
D11_GND: microcontroller.Pin  # GPIO11
D2: microcontroller.Pin  # GPIO2
CTS0: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO3
RTS0: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO4
TX1: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
RX1: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
CTS1: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
RTS1: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO8
D9: microcontroller.Pin  # GPIO9
D12: microcontroller.Pin  # GPIO12
SDA: microcontroller.Pin  # GPIO12
SDA0: microcontroller.Pin  # GPIO12
MISO1: microcontroller.Pin  # GPIO12
D13: microcontroller.Pin  # GPIO13
SCL: microcontroller.Pin  # GPIO13
SCL0: microcontroller.Pin  # GPIO13
CS1: microcontroller.Pin  # GPIO13
D14: microcontroller.Pin  # GPIO14
SDA1: microcontroller.Pin  # GPIO14
SCK1: microcontroller.Pin  # GPIO14
D15: microcontroller.Pin  # GPIO15
SCL1: microcontroller.Pin  # GPIO15
MOSI1: microcontroller.Pin  # GPIO15
D16: microcontroller.Pin  # GPIO16
D21: microcontroller.Pin  # GPIO21
CS: microcontroller.Pin  # GPIO21
CS0: microcontroller.Pin  # GPIO21
D23: microcontroller.Pin  # GPIO23
MOSI: microcontroller.Pin  # GPIO23
MOSI0: microcontroller.Pin  # GPIO23
D20: microcontroller.Pin  # GPIO20
MISO: microcontroller.Pin  # GPIO20
MISO0: microcontroller.Pin  # GPIO20
D22: microcontroller.Pin  # GPIO22
SCK: microcontroller.Pin  # GPIO22
SCK0: microcontroller.Pin  # GPIO22
A0: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
A0_D26: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
D27: microcontroller.Pin  # GPIO27
A1_D27: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
D28: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
D29: microcontroller.Pin  # GPIO29


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
