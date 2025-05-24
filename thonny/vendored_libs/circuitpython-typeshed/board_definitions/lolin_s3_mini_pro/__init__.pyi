# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LOLIN S3 MINI PRO 4MB Flash 2MB PSRAM
 - port: espressif
 - board_id: lolin_s3_mini_pro
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BOOT: microcontroller.Pin  # GPIO0
BUTTON0: microcontroller.Pin  # GPIO0
BUTTON1: microcontroller.Pin  # GPIO47
BUTTON2: microcontroller.Pin  # GPIO48
NEOPIXEL_ENABLE: microcontroller.Pin  # GPIO7
NEOPIXEL: microcontroller.Pin  # GPIO8
IR_LED: microcontroller.Pin  # GPIO9
SCL: microcontroller.Pin  # GPIO11
SDA: microcontroller.Pin  # GPIO12
IMU_INT1: microcontroller.Pin  # GPIO18
IMU_INT2: microcontroller.Pin  # GPIO21
TFT_DC: microcontroller.Pin  # GPIO36
TFT_CS: microcontroller.Pin  # GPIO35
TFT_RES: microcontroller.Pin  # GPIO34
TFT_BACKLIGHT: microcontroller.Pin  # GPIO33
CLK: microcontroller.Pin  # GPIO40
MOSI: microcontroller.Pin  # GPIO39
MISO: microcontroller.Pin  # GPIO38
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
