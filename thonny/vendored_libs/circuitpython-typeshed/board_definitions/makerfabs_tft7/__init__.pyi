# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for MakerFabs-ESP32-S3-Parallel-TFT-With-Touch-7inch
 - port: espressif
 - board_id: makerfabs_tft7
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dotclockframebuffer, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
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
TFT_BACKLIGHT: microcontroller.Pin  # GPIO10
GPIO20: microcontroller.Pin  # GPIO20
GPIO19: microcontroller.Pin  # GPIO19
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO20
I2S_WORD_SELECT: microcontroller.Pin  # GPIO2
I2S_DATA: microcontroller.Pin  # GPIO19
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
SCL: microcontroller.Pin  # GPIO18
SDA: microcontroller.Pin  # GPIO17
TOUCH_RESET: microcontroller.Pin  # GPIO38
SDIO_CLK: microcontroller.Pin  # GPIO12
SDIO_CMD: microcontroller.Pin  # GPIO11
SDIO_D0: microcontroller.Pin  # GPIO13
BUTTON: microcontroller.Pin  # GPIO1


# Members:
TFT_PINS: Dict[str, Any]

TFT_TIMINGS: Dict[str, Any]

TFT_TIMINGS800: Dict[str, Any]

TFT_TIMINGS1024: Dict[str, Any]

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#     { MP_ROM_QSTR(MP_QSTR_red), MP_ROM_PTR(&tft_r_pins) },
#     { MP_ROM_QSTR(MP_QSTR_green), MP_ROM_PTR(&tft_g_pins) },
#     { MP_ROM_QSTR(MP_QSTR_blue), MP_ROM_PTR(&tft_b_pins) },
