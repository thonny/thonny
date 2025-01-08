# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni PicoSystem
 - port: raspberrypi
 - board_id: pimoroni_picosystem
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: stage, ugame
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
VBUS_DETECT: microcontroller.Pin  # GPIO2
LCD_RESET: microcontroller.Pin  # GPIO4
LCD_CS: microcontroller.Pin  # GPIO5
LCD_SCLK: microcontroller.Pin  # GPIO6
LCD_MOSI: microcontroller.Pin  # GPIO7
LCD_VSYNC: microcontroller.Pin  # GPIO8
LCD_DC: microcontroller.Pin  # GPIO9
AUDIO: microcontroller.Pin  # GPIO11
BACKLIGHT: microcontroller.Pin  # GPIO12
LED_G: microcontroller.Pin  # GPIO13
LED_R: microcontroller.Pin  # GPIO14
LED_B: microcontroller.Pin  # GPIO15
SW_Y: microcontroller.Pin  # GPIO16
SW_X: microcontroller.Pin  # GPIO17
SW_A: microcontroller.Pin  # GPIO18
SW_B: microcontroller.Pin  # GPIO19
SW_DOWN: microcontroller.Pin  # GPIO20
SW_RIGHT: microcontroller.Pin  # GPIO21
SW_LEFT: microcontroller.Pin  # GPIO22
SW_UP: microcontroller.Pin  # GPIO23
CHARGE_STAT: microcontroller.Pin  # GPIO24
BAT_SENSE: microcontroller.Pin  # GPIO26


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
