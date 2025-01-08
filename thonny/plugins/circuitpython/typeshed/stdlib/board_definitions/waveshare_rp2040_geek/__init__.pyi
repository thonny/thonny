# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare RP2040-GEEK
 - port: raspberrypi
 - board_id: waveshare_rp2040_geek
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
GP22: microcontroller.Pin  # GPIO22
GP23: microcontroller.Pin  # GPIO23
GP25: microcontroller.Pin  # GPIO25
GP28: microcontroller.Pin  # GPIO28
GP29: microcontroller.Pin  # GPIO29
TX: microcontroller.Pin  # GPIO4
RX: microcontroller.Pin  # GPIO5
SCL: microcontroller.Pin  # GPIO29
SDA: microcontroller.Pin  # GPIO28
SD_SCK: microcontroller.Pin  # GPIO18
SD_MOSI: microcontroller.Pin  # GPIO19
SD_MISO: microcontroller.Pin  # GPIO20
SD_CS: microcontroller.Pin  # GPIO23
SDIO_CLK: microcontroller.Pin  # GPIO18
SDIO_COMMAND: microcontroller.Pin  # GPIO19
SDIO_DATA0: microcontroller.Pin  # GPIO20
SDIO_DATA1: microcontroller.Pin  # GPIO21
SDIO_DATA2: microcontroller.Pin  # GPIO22
SDIO_DATA3: microcontroller.Pin  # GPIO23
LCD_DC: microcontroller.Pin  # GPIO8
LCD_CS: microcontroller.Pin  # GPIO9
LCD_CLK: microcontroller.Pin  # GPIO10
LCD_MOSI: microcontroller.Pin  # GPIO11
LCD_RST: microcontroller.Pin  # GPIO12
LCD_BACKLIGHT: microcontroller.Pin  # GPIO25


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

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
