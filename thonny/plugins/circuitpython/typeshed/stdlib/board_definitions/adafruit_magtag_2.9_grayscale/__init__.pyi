# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit MagTag
 - port: espressif
 - board_id: adafruit_magtag_2.9_grayscale
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_display_text, adafruit_fakerequests, adafruit_lis3dh, adafruit_portalbase, adafruit_requests, neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
D10: microcontroller.Pin  # GPIO10
A1: microcontroller.Pin  # GPIO18
AD1: microcontroller.Pin  # GPIO18
LED: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
SPEAKER: microcontroller.Pin  # GPIO17
SPEAKER_ENABLE: microcontroller.Pin  # GPIO16
EPD_BUSY: microcontroller.Pin  # GPIO5
EPD_RESET: microcontroller.Pin  # GPIO6
EPD_DC: microcontroller.Pin  # GPIO7
EPD_CS: microcontroller.Pin  # GPIO8
EPD_MOSI: microcontroller.Pin  # GPIO35
EPD_SCK: microcontroller.Pin  # GPIO36
EPD_MISO: microcontroller.Pin  # GPIO37
BUTTON_A: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
BUTTON_B: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
BUTTON_C: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
BUTTON_D: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
BOOT0: microcontroller.Pin  # GPIO0
LIGHT: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO3
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO4
BATTERY: microcontroller.Pin  # GPIO4
SDA: microcontroller.Pin  # GPIO33
SCL: microcontroller.Pin  # GPIO34
NEOPIXEL_POWER_INVERTED: microcontroller.Pin  # GPIO21
NEOPIXEL_POWER: microcontroller.Pin  # GPIO21
NEOPIXEL: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # GPIO9


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
