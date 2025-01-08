# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Hardkernel Odroid Go
 - port: espressif
 - board_id: hardkernel_odroid_go
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
BATTERY: microcontroller.Pin  # GPIO36
BTN_START: microcontroller.Pin  # GPIO39
BTN_AXIS_X: microcontroller.Pin  # GPIO34
BTN_AXIS_Y: microcontroller.Pin  # GPIO35
BTN_A: microcontroller.Pin  # GPIO32
BTN_B: microcontroller.Pin  # GPIO33
SPEAKER_IN_M: microcontroller.Pin  # GPIO25
SPEAKER_IN_P: microcontroller.Pin  # GPIO26
BTN_SELECT: microcontroller.Pin  # GPIO27
BACKLIGHT_PWM: microcontroller.Pin  # GPIO14
EXT3: microcontroller.Pin  # GPIO12
BTN_MENU: microcontroller.Pin  # GPIO13
MOSI: microcontroller.Pin  # GPIO23
EXT8: microcontroller.Pin  # GPIO23
SD_CS: microcontroller.Pin  # GPIO22
MISO: microcontroller.Pin  # GPIO19
EXT7: microcontroller.Pin  # GPIO19
SCK: microcontroller.Pin  # GPIO18
EXT2: microcontroller.Pin  # GPIO18
LCD_CS: microcontroller.Pin  # GPIO5
EXT5: microcontroller.Pin  # GPIO4
BTN_VOLUME: microcontroller.Pin  # GPIO0
LED: microcontroller.Pin  # GPIO2
EXT4: microcontroller.Pin  # GPIO15


# Members:
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
