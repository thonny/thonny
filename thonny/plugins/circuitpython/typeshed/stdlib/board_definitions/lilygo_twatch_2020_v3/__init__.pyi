# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Lilygo T-watch 2020 V3
 - port: espressif
 - board_id: lilygo_twatch_2020_v3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
VIBRATE: microcontroller.Pin  # GPIO4
I2S_SCK: microcontroller.Pin  # GPIO26
I2S_WS: microcontroller.Pin  # GPIO25
I2S_OUT: microcontroller.Pin  # GPIO33
PDM_CLK: microcontroller.Pin  # GPIO0
PDM_DATA: microcontroller.Pin  # GPIO2
IR_LED: microcontroller.Pin  # GPIO13
SCL: microcontroller.Pin  # GPIO22
SDA: microcontroller.Pin  # GPIO21
BMA423_INT: microcontroller.Pin  # GPIO39
PCF8563_INT: microcontroller.Pin  # GPIO37
AXP202_INT: microcontroller.Pin  # GPIO35
TOUCH_SCL: microcontroller.Pin  # GPIO32
TOUCH_SDA: microcontroller.Pin  # GPIO23
TOUCH_RST: microcontroller.Pin  # GPIO14
TOUCH_INT: microcontroller.Pin  # GPIO38
LCD_CLK: microcontroller.Pin  # GPIO18
LCD_MOSI: microcontroller.Pin  # GPIO19
LCD_DC: microcontroller.Pin  # GPIO27
LCD_CS: microcontroller.Pin  # GPIO5
LCD_BRIGHTNESS: microcontroller.Pin  # GPIO15


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def LCD_SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
