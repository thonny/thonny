# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pajenicko PicoPad
 - port: raspberrypi
 - board_id: pajenicko_picopad
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, cyw43, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: stage, ugame
"""

# Imports
import busio
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
GP26: microcontroller.Pin  # GPIO26
GP27: microcontroller.Pin  # GPIO27
GP28: microcontroller.Pin  # GPIO28
D0: microcontroller.Pin  # GPIO26
D1: microcontroller.Pin  # GPIO14
D2: microcontroller.Pin  # GPIO1
D3: microcontroller.Pin  # GPIO0
D4: microcontroller.Pin  # GPIO27
D5: microcontroller.Pin  # GPIO28
A0: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
LCD_RESET: microcontroller.Pin  # GPIO20
LCD_CS: microcontroller.Pin  # GPIO21
LCD_SCLK: microcontroller.Pin  # GPIO18
LCD_MOSI: microcontroller.Pin  # GPIO19
LCD_DC: microcontroller.Pin  # GPIO17
LCD_BL: microcontroller.Pin  # GPIO16
AUDIO: microcontroller.Pin  # GPIO15
LED: microcontroller.Pin  # GPIO22
SW_X: microcontroller.Pin  # GPIO9
SW_Y: microcontroller.Pin  # GPIO8
SW_A: microcontroller.Pin  # GPIO7
SW_B: microcontroller.Pin  # GPIO6
SW_DOWN: microcontroller.Pin  # GPIO5
SW_RIGHT: microcontroller.Pin  # GPIO2
SW_LEFT: microcontroller.Pin  # GPIO3
SW_UP: microcontroller.Pin  # GPIO4
SD_CS: microcontroller.Pin  # GPIO13
SD_SCK: microcontroller.Pin  # GPIO10
SD_MOSI: microcontroller.Pin  # GPIO11
SD_MISO: microcontroller.Pin  # GPIO12
BAT_SENSE: microcontroller.Pin  # GPIO29
TX: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
SDA: microcontroller.Pin  # GPIO0
SCL: microcontroller.Pin  # GPIO1
SDA_ALT: microcontroller.Pin  # GPIO14
SCL_ALT: microcontroller.Pin  # GPIO27
SMPS_MODE: microcontroller.Pin  # CYW1
LED: microcontroller.Pin  # CYW0
VBUS_SENSE: microcontroller.Pin  # CYW2


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def I2C_ALT() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
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
