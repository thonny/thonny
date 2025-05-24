# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare ESP32-S3-Matrix
 - port: espressif
 - board_id: waveshare_esp32_s3_matrix
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO7: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
IO6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
IO4: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
IO3: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
IO2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
I01: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
IO33: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
IO34: microcontroller.Pin  # GPIO34
D34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
D37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
D38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
D39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
D40: microcontroller.Pin  # GPIO40
IO43: microcontroller.Pin  # GPIO43
D43: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
D44: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
IO14: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
NEOPIXEL: microcontroller.Pin  # GPIO14
IMU_SDA: microcontroller.Pin  # GPIO11
IMU_SCL: microcontroller.Pin  # GPIO12
IMU_INT1: microcontroller.Pin  # GPIO10
IMU_INT2: microcontroller.Pin  # GPIO13


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
