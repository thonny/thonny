# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Cytron Maker Uno RP2040
 - port: raspberrypi
 - board_id: cytron_maker_uno_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: neopixel, simpleio
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
LED0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
GP1: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
LED1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
LED2: microcontroller.Pin  # GPIO2
BUTTON: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
LED3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
LED4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
LED5: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
LED6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
LED7: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
LED8: microcontroller.Pin  # GPIO8
BUZZER: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
LED9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
D10: microcontroller.Pin  # GPIO10
LED10: microcontroller.Pin  # GPIO10
SCK: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
LED11: microcontroller.Pin  # GPIO11
MOSI: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
LED12: microcontroller.Pin  # GPIO12
MISO: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
LED13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
SERVO1: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
SERVO2: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
SERVO3: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
SERVO4: microcontroller.Pin  # GPIO17
GP20: microcontroller.Pin  # GPIO20
D20: microcontroller.Pin  # GPIO20
LED20: microcontroller.Pin  # GPIO20
SDA: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
LED21: microcontroller.Pin  # GPIO21
SCL: microcontroller.Pin  # GPIO21
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
GP29_A3: microcontroller.Pin  # GPIO29
GP29: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29
GP25: microcontroller.Pin  # GPIO25
NEOPIXEL: microcontroller.Pin  # GPIO25
RGB: microcontroller.Pin  # GPIO25


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
