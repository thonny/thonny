# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for TinyWATCH S3
 - port: espressif
 - board_id: unexpectedmaker_tinywatch_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_st7789
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
USER_BUTTON: microcontroller.Pin  # GPIO0
BUZZER: microcontroller.Pin  # GPIO18
MO: microcontroller.Pin  # GPIO35
MI: microcontroller.Pin  # GPIO37
CLK: microcontroller.Pin  # GPIO36
TFT_CS: microcontroller.Pin  # GPIO16
TFT_DC: microcontroller.Pin  # GPIO15
TFT_RESET: microcontroller.Pin  # GPIO17
TFT_BACKLIGHT: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
SDA2: microcontroller.Pin  # GPIO5
SCL2: microcontroller.Pin  # GPIO10
TOUCH_INT: microcontroller.Pin  # GPIO11
TOUCH_RESET: microcontroller.Pin  # GPIO12
RTC_INT: microcontroller.Pin  # GPIO4
FG_ALERT: microcontroller.Pin  # GPIO14
BMI_INT1: microcontroller.Pin  # GPIO6
BMI_INT2: microcontroller.Pin  # GPIO7
I2S_MIC_DATA: microcontroller.Pin  # GPIO1
I2S_MIC_BCLK: microcontroller.Pin  # GPIO2
I2S_MIC_WS: microcontroller.Pin  # GPIO3
USER_PWR_SHUTDOWN: microcontroller.Pin  # GPIO21
EXT_FLASH_CS: microcontroller.Pin  # GPIO33
VBUS_SENSE: microcontroller.Pin  # GPIO34


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
