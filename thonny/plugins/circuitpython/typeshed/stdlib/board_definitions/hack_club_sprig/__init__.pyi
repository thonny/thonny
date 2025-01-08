# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Hack Club Sprig
 - port: raspberrypi
 - board_id: hack_club_sprig
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import displayio
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
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
GP22: microcontroller.Pin  # GPIO22
SMPS_MODE: microcontroller.Pin  # GPIO23
GP23: microcontroller.Pin  # GPIO23
VBUS_SENSE: microcontroller.Pin  # GPIO24
GP24: microcontroller.Pin  # GPIO24
LED: microcontroller.Pin  # GPIO25
GP25: microcontroller.Pin  # GPIO25
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29
BLUE_LED: microcontroller.Pin  # GPIO4
BUTTON_W: microcontroller.Pin  # GPIO5
BUTTON_A: microcontroller.Pin  # GPIO6
BUTTON_S: microcontroller.Pin  # GPIO7
BUTTON_D: microcontroller.Pin  # GPIO8
AUDIO_DIN: microcontroller.Pin  # GPIO9
AUDIO_BCLK: microcontroller.Pin  # GPIO10
AUDIO_LRCLK: microcontroller.Pin  # GPIO11
BUTTON_I: microcontroller.Pin  # GPIO12
BUTTON_J: microcontroller.Pin  # GPIO13
BUTTON_K: microcontroller.Pin  # GPIO14
BUTTON_L: microcontroller.Pin  # GPIO15
MISO: microcontroller.Pin  # GPIO16
TFT_LITE: microcontroller.Pin  # GPIO17
SCK: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO19
TFT_CS: microcontroller.Pin  # GPIO20
CARD_CS: microcontroller.Pin  # GPIO21
TFT_DC: microcontroller.Pin  # GPIO22
TFT_RESET: microcontroller.Pin  # GPIO23
WHITE_LED: microcontroller.Pin  # GPIO28


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
