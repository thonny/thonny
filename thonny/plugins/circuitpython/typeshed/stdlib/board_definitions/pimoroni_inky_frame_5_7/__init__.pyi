# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Inky Frame 5.7
 - port: raspberrypi
 - board_id: pimoroni_inky_frame_5_7
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, cyw43, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_register, adafruit_sdcard, pcf85063a
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
I2C_INT: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO5
LED_ACT: microcontroller.Pin  # GPIO6
LED: microcontroller.Pin  # GPIO6
LED_CONN: microcontroller.Pin  # GPIO7
SWITCH_CLK: microcontroller.Pin  # GPIO8
SWITCH_LATCH: microcontroller.Pin  # GPIO9
SWITCH_OUT: microcontroller.Pin  # GPIO10
LED_A: microcontroller.Pin  # GPIO11
LED_B: microcontroller.Pin  # GPIO12
LED_C: microcontroller.Pin  # GPIO13
LED_D: microcontroller.Pin  # GPIO14
LED_E: microcontroller.Pin  # GPIO15
MISO: microcontroller.Pin  # GPIO16
INKY_CS: microcontroller.Pin  # GPIO17
SCLK: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO19
SD_DAT1: microcontroller.Pin  # GPIO20
SD_DAT2: microcontroller.Pin  # GPIO21
SD_CS: microcontroller.Pin  # GPIO22
A0: microcontroller.Pin  # GPIO26
INKY_RES: microcontroller.Pin  # GPIO27
INKY_DC: microcontroller.Pin  # GPIO28
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29
PICO_LED: microcontroller.Pin  # CYW0
SMPS_MODE: microcontroller.Pin  # CYW1
VBUS_SENSE: microcontroller.Pin  # CYW2


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
