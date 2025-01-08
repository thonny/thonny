# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Diodes Delight Piunora
 - port: broadcom
 - board_id: diodes_delight_piunora
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
GPIO5: microcontroller.Pin  # GPIO5
D0: microcontroller.Pin  # GPIO5
RX: microcontroller.Pin  # GPIO5
GPIO4: microcontroller.Pin  # GPIO4
D1: microcontroller.Pin  # GPIO4
TX: microcontroller.Pin  # GPIO4
GPIO18: microcontroller.Pin  # GPIO18
D2: microcontroller.Pin  # GPIO18
GPIO19: microcontroller.Pin  # GPIO19
D3: microcontroller.Pin  # GPIO19
GPIO20: microcontroller.Pin  # GPIO20
D4: microcontroller.Pin  # GPIO20
GPIO21: microcontroller.Pin  # GPIO21
D5: microcontroller.Pin  # GPIO21
GPIO22: microcontroller.Pin  # GPIO22
D6: microcontroller.Pin  # GPIO22
SDA6: microcontroller.Pin  # GPIO22
GPIO23: microcontroller.Pin  # GPIO23
D7: microcontroller.Pin  # GPIO23
SCL6: microcontroller.Pin  # GPIO23
GPIO6: microcontroller.Pin  # GPIO6
D8: microcontroller.Pin  # GPIO6
SDA4: microcontroller.Pin  # GPIO6
GPIO7: microcontroller.Pin  # GPIO7
D9: microcontroller.Pin  # GPIO7
SCL4: microcontroller.Pin  # GPIO7
SPI0_CE1: microcontroller.Pin  # GPIO7
GPIO8: microcontroller.Pin  # GPIO8
D10: microcontroller.Pin  # GPIO8
SPI0_CE0: microcontroller.Pin  # GPIO8
GPIO10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO10
SPI0_MOSI: microcontroller.Pin  # GPIO10
GPIO9: microcontroller.Pin  # GPIO9
D12: microcontroller.Pin  # GPIO9
SPI0_MISO: microcontroller.Pin  # GPIO9
GPIO11: microcontroller.Pin  # GPIO11
D13: microcontroller.Pin  # GPIO11
SPI0_SCLK: microcontroller.Pin  # GPIO11
SDA: microcontroller.Pin  # GPIO2
SDA1: microcontroller.Pin  # GPIO2
SCL: microcontroller.Pin  # GPIO3
GPIO12: microcontroller.Pin  # GPIO12
NEOPIXEL: microcontroller.Pin  # GPIO12


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
