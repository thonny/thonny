# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for EncoderPad RP2040
 - port: raspberrypi
 - board_id: jpconstantineau_encoderpad_rp2040
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
KEY1: microcontroller.Pin  # GPIO14
KEY2: microcontroller.Pin  # GPIO18
KEY3: microcontroller.Pin  # GPIO19
KEY4: microcontroller.Pin  # GPIO20
KEY5: microcontroller.Pin  # GPIO0
KEY6: microcontroller.Pin  # GPIO1
KEY7: microcontroller.Pin  # GPIO2
KEY8: microcontroller.Pin  # GPIO3
KEY9: microcontroller.Pin  # GPIO4
LED: microcontroller.Pin  # GPIO25
SPEAKER: microcontroller.Pin  # GPIO13
ENCODER_A: microcontroller.Pin  # GPIO5
ROTA: microcontroller.Pin  # GPIO5
ENCODER_B: microcontroller.Pin  # GPIO6
ROTB: microcontroller.Pin  # GPIO6
NEOPIXEL: microcontroller.Pin  # GPIO15
SDA: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
SCK: microcontroller.Pin  # GPIO26
MOSI: microcontroller.Pin  # GPIO27
MISO: microcontroller.Pin  # GPIO28
CS: microcontroller.Pin  # GPIO29


# Members:
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
