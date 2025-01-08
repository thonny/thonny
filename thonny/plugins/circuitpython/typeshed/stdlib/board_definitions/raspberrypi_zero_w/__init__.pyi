# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Raspberry Pi Zero W
 - port: broadcom
 - board_id: raspberrypi_zero_w
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, array, atexit, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, rainbowio, random, re, rtc, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, videocore, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO2
SDA: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO3
SCL: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
CE1: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO8
CE0: microcontroller.Pin  # GPIO8
D9: microcontroller.Pin  # GPIO9
MISO: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
MOSI: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
SCLK: microcontroller.Pin  # GPIO11
SCK: microcontroller.Pin  # GPIO11
D12: microcontroller.Pin  # GPIO12
D13: microcontroller.Pin  # GPIO13
D14: microcontroller.Pin  # GPIO14
TXD: microcontroller.Pin  # GPIO14
D15: microcontroller.Pin  # GPIO15
RXD: microcontroller.Pin  # GPIO15
TX: microcontroller.Pin  # GPIO14
RX: microcontroller.Pin  # GPIO15
D16: microcontroller.Pin  # GPIO16
D17: microcontroller.Pin  # GPIO17
D18: microcontroller.Pin  # GPIO18
D19: microcontroller.Pin  # GPIO19
MISO_1: microcontroller.Pin  # GPIO19
D20: microcontroller.Pin  # GPIO20
MOSI_1: microcontroller.Pin  # GPIO20
D21: microcontroller.Pin  # GPIO21
SCLK_1: microcontroller.Pin  # GPIO21
SCK_1: microcontroller.Pin  # GPIO21
D22: microcontroller.Pin  # GPIO22
D23: microcontroller.Pin  # GPIO23
D24: microcontroller.Pin  # GPIO24
D25: microcontroller.Pin  # GPIO25
D26: microcontroller.Pin  # GPIO26
D27: microcontroller.Pin  # GPIO27


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
