# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO TTGO T-DISPLAY v1.1 4M
 - port: espressif
 - board_id: lilygo_ttgo_tdisplay_esp32_4m
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON0: microcontroller.Pin  # GPIO0
IO0: microcontroller.Pin  # GPIO0
BUTTON1: microcontroller.Pin  # GPIO35
IO35: microcontroller.Pin  # GPIO35
IO2: microcontroller.Pin  # GPIO2
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO15: microcontroller.Pin  # GPIO15
IO17: microcontroller.Pin  # GPIO17
IO21: microcontroller.Pin  # GPIO21
IO22: microcontroller.Pin  # GPIO22
IO25: microcontroller.Pin  # GPIO25
IO26: microcontroller.Pin  # GPIO26
IO27: microcontroller.Pin  # GPIO27
IO32: microcontroller.Pin  # GPIO32
IO33: microcontroller.Pin  # GPIO33
IO36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
LCD_MOSI: microcontroller.Pin  # GPIO19
LCD_CLK: microcontroller.Pin  # GPIO18
LCD_CS: microcontroller.Pin  # GPIO5
LCD_RST: microcontroller.Pin  # GPIO23
LCD_BCKL: microcontroller.Pin  # GPIO4
LCD_D_C: microcontroller.Pin  # GPIO16
BATTERY: microcontroller.Pin  # GPIO34


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
