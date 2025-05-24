# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Dial
 - port: espressif
 - board_id: m5stack_dial
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
PORTA_SCL: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
PORTA_SDA: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
PORTB_IN: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
PORTB_OUT: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
ENC_A: microcontroller.Pin  # GPIO41
ENC_B: microcontroller.Pin  # GPIO40
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
NEOPIXEL: microcontroller.Pin  # GPIO21
TOUCH_IRQ: microcontroller.Pin  # GPIO14
RFID_IRQ: microcontroller.Pin  # GPIO10
SDA: microcontroller.Pin  # GPIO11
SCL: microcontroller.Pin  # GPIO12
SPEAKER: microcontroller.Pin  # GPIO3
KNOB_BUTTON: microcontroller.Pin  # GPIO42
POWER_HOLD: microcontroller.Pin  # GPIO46
SCK: microcontroller.Pin  # GPIO6
MOSI: microcontroller.Pin  # GPIO5
TFT_CS: microcontroller.Pin  # GPIO7
TFT_DC: microcontroller.Pin  # GPIO4
TFT_RESET: microcontroller.Pin  # GPIO8
TFT_BACKLIGHT: microcontroller.Pin  # GPIO9


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
