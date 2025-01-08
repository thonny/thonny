# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for E-Fidget
 - port: raspberrypi
 - board_id: e_fidget
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO0
GP1: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
BTN1: microcontroller.Pin  # GPIO3
BTN3: microcontroller.Pin  # GPIO4
BTN2: microcontroller.Pin  # GPIO5
M1: microcontroller.Pin  # GPIO7
M2: microcontroller.Pin  # GPIO11
M3: microcontroller.Pin  # GPIO13
M4: microcontroller.Pin  # GPIO9
M5: microcontroller.Pin  # GPIO8
M6: microcontroller.Pin  # GPIO10
M7: microcontroller.Pin  # GPIO12
M8: microcontroller.Pin  # GPIO14
NEOPIXEL: microcontroller.Pin  # GPIO18
SMPS_MODE: microcontroller.Pin  # GPIO23
VBUS_SENSE: microcontroller.Pin  # GPIO24
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29


# Members:

# Unmapped:
#   none
