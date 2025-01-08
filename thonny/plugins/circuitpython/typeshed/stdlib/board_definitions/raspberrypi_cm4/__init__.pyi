# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Raspberry Pi Compute Module 4
 - port: broadcom
 - board_id: raspberrypi_cm4
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, array, atexit, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, rainbowio, random, re, rtc, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, videocore, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
ID_SD: microcontroller.Pin  # GPIO0
ID_SC: microcontroller.Pin  # GPIO1
GPIO2: microcontroller.Pin  # GPIO2
GPIO3: microcontroller.Pin  # GPIO3
GPIO4: microcontroller.Pin  # GPIO4
GPIO5: microcontroller.Pin  # GPIO5
GPIO6: microcontroller.Pin  # GPIO6
GPIO7: microcontroller.Pin  # GPIO7
GPIO8: microcontroller.Pin  # GPIO8
GPIO9: microcontroller.Pin  # GPIO9
GPIO10: microcontroller.Pin  # GPIO10
GPIO11: microcontroller.Pin  # GPIO11
GPIO12: microcontroller.Pin  # GPIO12
GPIO13: microcontroller.Pin  # GPIO13
GPIO14: microcontroller.Pin  # GPIO14
GPIO15: microcontroller.Pin  # GPIO15
GPIO16: microcontroller.Pin  # GPIO16
GPIO17: microcontroller.Pin  # GPIO17
GPIO18: microcontroller.Pin  # GPIO18
GPIO19: microcontroller.Pin  # GPIO19
GPIO20: microcontroller.Pin  # GPIO20
GPIO21: microcontroller.Pin  # GPIO21
GPIO22: microcontroller.Pin  # GPIO22
GPIO23: microcontroller.Pin  # GPIO23
GPIO24: microcontroller.Pin  # GPIO24
GPIO25: microcontroller.Pin  # GPIO25
GPIO26: microcontroller.Pin  # GPIO26
GPIO27: microcontroller.Pin  # GPIO27
LED_nACT: microcontroller.Pin  # GPIO42
LED: microcontroller.Pin  # GPIO42
SDA0: microcontroller.Pin  # GPIO44
SCL0: microcontroller.Pin  # GPIO45


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
