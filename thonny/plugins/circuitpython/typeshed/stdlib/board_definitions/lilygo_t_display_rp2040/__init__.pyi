# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO T-DISPLAY
 - port: raspberrypi
 - board_id: lilygo_t_display_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO2
GP2: microcontroller.Pin  # GPIO2
BUTTON0: microcontroller.Pin  # GPIO6
BUTTON_L: microcontroller.Pin  # GPIO6
GP6: microcontroller.Pin  # GPIO6
BUTTON1: microcontroller.Pin  # GPIO7
BUTTON_R: microcontroller.Pin  # GPIO7
GP7: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
SCK: microcontroller.Pin  # GPIO10
GP10: microcontroller.Pin  # GPIO10
MOSI: microcontroller.Pin  # GPIO11
GP11: microcontroller.Pin  # GPIO11
MISO: microcontroller.Pin  # GPIO12
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO14
GP14: microcontroller.Pin  # GPIO14
SCL: microcontroller.Pin  # GPIO15
GP15: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
TFT_POWER: microcontroller.Pin  # GPIO22
GP22: microcontroller.Pin  # GPIO22
GP23: microcontroller.Pin  # GPIO23
GP24: microcontroller.Pin  # GPIO24
LED: microcontroller.Pin  # GPIO25
GP25: microcontroller.Pin  # GPIO25
GP27: microcontroller.Pin  # GPIO27
GP28: microcontroller.Pin  # GPIO28
GP29: microcontroller.Pin  # GPIO29
LCD_MOSI: microcontroller.Pin  # GPIO3
LCD_CLK: microcontroller.Pin  # GPIO2
LCD_CS: microcontroller.Pin  # GPIO5
LCD_RESET: microcontroller.Pin  # GPIO0
LCD_BACKLIGHT: microcontroller.Pin  # GPIO4
LCD_DC: microcontroller.Pin  # GPIO1
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO26


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
