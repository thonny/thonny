# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Arduino Nano RP2040 Connect
 - port: raspberrypi
 - board_id: arduino_nano_rp2040_connect
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
ESP_GPIO0: microcontroller.Pin  # GPIO2
ESP_RESET: microcontroller.Pin  # GPIO3
ESP_BUSY: microcontroller.Pin  # GPIO10
ESP_CS: microcontroller.Pin  # GPIO9
LED: microcontroller.Pin  # GPIO6
D13: microcontroller.Pin  # GPIO6
SCK: microcontroller.Pin  # GPIO6
D12: microcontroller.Pin  # GPIO4
MISO: microcontroller.Pin  # GPIO4
D11: microcontroller.Pin  # GPIO7
MOSI: microcontroller.Pin  # GPIO7
D10: microcontroller.Pin  # GPIO5
MISO1: microcontroller.Pin  # GPIO8
MOSI1: microcontroller.Pin  # GPIO11
SCK1: microcontroller.Pin  # GPIO14
CS1: microcontroller.Pin  # GPIO9
A4: microcontroller.Pin  # GPIO12
SDA: microcontroller.Pin  # GPIO12
A5: microcontroller.Pin  # GPIO13
SCL: microcontroller.Pin  # GPIO13
D3: microcontroller.Pin  # GPIO15
D4: microcontroller.Pin  # GPIO16
D5: microcontroller.Pin  # GPIO17
D6: microcontroller.Pin  # GPIO18
D7: microcontroller.Pin  # GPIO19
D8: microcontroller.Pin  # GPIO20
D9: microcontroller.Pin  # GPIO21
MICROPHONE_DATA: microcontroller.Pin  # GPIO22
MICROPHONE_CLOCK: microcontroller.Pin  # GPIO23
INT1: microcontroller.Pin  # GPIO24
D2: microcontroller.Pin  # GPIO25
A0: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29


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
