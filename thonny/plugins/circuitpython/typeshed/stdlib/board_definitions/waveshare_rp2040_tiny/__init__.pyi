# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare RP2040-Tiny
 - port: raspberrypi
 - board_id: waveshare_rp2040_tiny
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
GP1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
NEOPIXEL: microcontroller.Pin  # GPIO16
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
GP29_A3: microcontroller.Pin  # GPIO29
GP29: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
