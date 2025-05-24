# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Sunton-ESP32-8048S050
 - port: espressif
 - board_id: sunton_esp32_8048S050
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dotclockframebuffer, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller
from typing import Any, Dict


# Board Info:
board_id: str


# Pins:
de: microcontroller.Pin  # GPIO40
vsync: microcontroller.Pin  # GPIO41
hsync: microcontroller.Pin  # GPIO39
dclk: microcontroller.Pin  # GPIO42
TFT_BACKLIGHT: microcontroller.Pin  # GPIO2
IO0: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
BUTTON: microcontroller.Pin  # GPIO0
IO19: microcontroller.Pin  # GPIO19
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO20: microcontroller.Pin  # GPIO20
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
SDA: microcontroller.Pin  # GPIO19
SCL: microcontroller.Pin  # GPIO20
MOSI: microcontroller.Pin  # GPIO11
SCK: microcontroller.Pin  # GPIO12
MISO: microcontroller.Pin  # GPIO13
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO0
I2S_WORD_SELECT: microcontroller.Pin  # GPIO18
I2S_DATA: microcontroller.Pin  # GPIO17
TOUCH_RESET: microcontroller.Pin  # GPIO38
TOUCH_CS: microcontroller.Pin  # GPIO38
TOUCH_INT: microcontroller.Pin  # GPIO18
SD_CS: microcontroller.Pin  # GPIO10


# Members:
TFT_PINS: Dict[str, Any]

TFT_TIMINGS: Dict[str, Any]

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
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
#     { MP_ROM_QSTR(MP_QSTR_red), MP_ROM_PTR(&tft_r_pins) },
#     { MP_ROM_QSTR(MP_QSTR_green), MP_ROM_PTR(&tft_g_pins) },
#     { MP_ROM_QSTR(MP_QSTR_blue), MP_ROM_PTR(&tft_b_pins) },
