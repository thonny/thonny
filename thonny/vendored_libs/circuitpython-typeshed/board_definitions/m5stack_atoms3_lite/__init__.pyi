# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack AtomS3 Lite
 - port: espressif
 - board_id: m5stack_atoms3_lite
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
PORTA_SCL: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
PORTA_SDA: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
A4: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
D39: microcontroller.Pin  # GPIO39
D38: microcontroller.Pin  # GPIO38
NEOPIXEL: microcontroller.Pin  # GPIO35
BTN: microcontroller.Pin  # GPIO41
IR_LED: microcontroller.Pin  # GPIO4


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
