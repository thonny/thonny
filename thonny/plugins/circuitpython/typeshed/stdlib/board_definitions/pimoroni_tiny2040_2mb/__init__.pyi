# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Tiny 2040 (2MB)
 - port: raspberrypi
 - board_id: pimoroni_tiny2040_2mb
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
GP3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
LED_R: microcontroller.Pin  # GPIO18
LED_G: microcontroller.Pin  # GPIO19
LED_B: microcontroller.Pin  # GPIO20
USER_SW: microcontroller.Pin  # GPIO23
A0: microcontroller.Pin  # GPIO26
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
GP29_A3: microcontroller.Pin  # GPIO29
GP29: microcontroller.Pin  # GPIO29


# Members:

# Unmapped:
#   none
