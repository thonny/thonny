# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for 8086 USB Interposer
 - port: raspberrypi
 - board_id: 8086_usb_interposer
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
ADC_VBUS_IN: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
ADC_VBUS_OUT: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
LED: microcontroller.Pin  # GPIO7
LED_TOP_RED: microcontroller.Pin  # GPIO7
GP7: microcontroller.Pin  # GPIO7
LED_TOP_AMBER: microcontroller.Pin  # GPIO8
GP8: microcontroller.Pin  # GPIO8
LED_BOTTOM_RED: microcontroller.Pin  # GPIO22
GP22: microcontroller.Pin  # GPIO22
LED_BOTTOM_AMBER: microcontroller.Pin  # GPIO23
GP23: microcontroller.Pin  # GPIO23
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
SDA: microcontroller.Pin  # GPIO14
GP14: microcontroller.Pin  # GPIO14
SCL: microcontroller.Pin  # GPIO15
GP15: microcontroller.Pin  # GPIO15
BUTTON: microcontroller.Pin  # GPIO12
BOOT: microcontroller.Pin  # GPIO12
GP12: microcontroller.Pin  # GPIO12
USB_HOST_DATA_PLUS: microcontroller.Pin  # GPIO16
USB_HOST_DATA_MINUS: microcontroller.Pin  # GPIO17
USB_HOST_5V_POWER: microcontroller.Pin  # GPIO18


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
