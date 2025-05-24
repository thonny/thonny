# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO T-DISPLAY S3 v1.2
 - port: espressif
 - board_id: lilygo_tdisplay_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
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
BUTTON1: microcontroller.Pin  # GPIO14
IO14: microcontroller.Pin  # GPIO14
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO43: microcontroller.Pin  # GPIO43
STEMMA_SDA: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
STEMMA_SCL: microcontroller.Pin  # GPIO44
IO18: microcontroller.Pin  # GPIO18
TOUCH_SDA: microcontroller.Pin  # GPIO18
IO17: microcontroller.Pin  # GPIO17
TOUCH_SCL: microcontroller.Pin  # GPIO17
IO21: microcontroller.Pin  # GPIO21
TOUCH_RES: microcontroller.Pin  # GPIO21
IO16: microcontroller.Pin  # GPIO16
TOUCH_INT: microcontroller.Pin  # GPIO16
LCD_BCKL: microcontroller.Pin  # GPIO38
LCD_D0: microcontroller.Pin  # GPIO39
LCD_D1: microcontroller.Pin  # GPIO40
LCD_D2: microcontroller.Pin  # GPIO41
LCD_D3: microcontroller.Pin  # GPIO42
LCD_D4: microcontroller.Pin  # GPIO45
LCD_D5: microcontroller.Pin  # GPIO46
LCD_D6: microcontroller.Pin  # GPIO47
LCD_D7: microcontroller.Pin  # GPIO48
LCD_WR: microcontroller.Pin  # GPIO8
LCD_RD: microcontroller.Pin  # GPIO9
LCD_DC: microcontroller.Pin  # GPIO7
LCD_CS: microcontroller.Pin  # GPIO6
LCD_RST: microcontroller.Pin  # GPIO5
LCD_POWER_ON: microcontroller.Pin  # GPIO15
BATTERY: microcontroller.Pin  # GPIO4


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
