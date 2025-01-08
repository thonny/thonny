# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Feather MIMXRT1011
 - port: mimxrt10xx
 - board_id: feather_mimxrt1011
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_esp32spi, adafruit_requests
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO_AD_14
A1: microcontroller.Pin  # GPIO_AD_11
A2: microcontroller.Pin  # GPIO_AD_10
A3: microcontroller.Pin  # GPIO_AD_09
A4: microcontroller.Pin  # GPIO_AD_08
A5: microcontroller.Pin  # GPIO_AD_07
D5: microcontroller.Pin  # GPIO_06
D6: microcontroller.Pin  # GPIO_05
D9: microcontroller.Pin  # GPIO_04
D10: microcontroller.Pin  # GPIO_03
D11: microcontroller.Pin  # GPIO_02
D12: microcontroller.Pin  # GPIO_01
LED: microcontroller.Pin  # GPIO_00
D13: microcontroller.Pin  # GPIO_00
D14: microcontroller.Pin  # GPIO_AD_05
SCK: microcontroller.Pin  # GPIO_AD_06
MISO: microcontroller.Pin  # GPIO_AD_03
MOSI: microcontroller.Pin  # GPIO_AD_04
TX: microcontroller.Pin  # GPIO_AD_02
RX: microcontroller.Pin  # GPIO_AD_01
SDA: microcontroller.Pin  # GPIO_09
SCL: microcontroller.Pin  # GPIO_10
ESP_CS: microcontroller.Pin  # GPIO_13
ESP_GPIO0: microcontroller.Pin  # GPIO_07
ESP_BUSY: microcontroller.Pin  # GPIO_08
ESP_RESET: microcontroller.Pin  # GPIO_AD_00
ESP_TX: microcontroller.Pin  # GPIO_12
ESP_RX: microcontroller.Pin  # GPIO_11
NEOPIXEL: microcontroller.Pin  # GPIO_SD_05


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
