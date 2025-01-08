# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for uGame22
 - port: raspberrypi
 - board_id: ugame22
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: pew, stage, ugame
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TFT_RST: microcontroller.Pin  # GPIO1
TFT_SCK: microcontroller.Pin  # GPIO2
TFT_MOSI: microcontroller.Pin  # GPIO3
TFT_DC: microcontroller.Pin  # GPIO4
TFT_CS: microcontroller.Pin  # GPIO5
BUTTON_Z: microcontroller.Pin  # GPIO0
BUTTON_X: microcontroller.Pin  # GPIO6
BUTTON_DOWN: microcontroller.Pin  # GPIO7
BUTTON_O: microcontroller.Pin  # GPIO8
BUTTON_RIGHT: microcontroller.Pin  # GPIO9
BUTTON_UP: microcontroller.Pin  # GPIO10
BUTTON_LEFT: microcontroller.Pin  # GPIO11
GAIN: microcontroller.Pin  # GPIO22
I2S_DIN: microcontroller.Pin  # GPIO23
I2S_BCLK: microcontroller.Pin  # GPIO24
I2S_LRCLK: microcontroller.Pin  # GPIO25
SDA: microcontroller.Pin  # GPIO14
SCL: microcontroller.Pin  # GPIO15


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
