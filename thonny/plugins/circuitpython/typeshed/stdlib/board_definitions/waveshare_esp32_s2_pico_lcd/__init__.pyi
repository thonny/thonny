# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare ESP32-S2-Pico-LCD
 - port: espressif
 - board_id: waveshare_esp32_s2_pico_lcd
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
A3: microcontroller.Pin  # GPIO1
USB_IN: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
A0: microcontroller.Pin  # GPIO6
GP6: microcontroller.Pin  # GPIO6
A1: microcontroller.Pin  # GPIO7
GP7: microcontroller.Pin  # GPIO7
A2: microcontroller.Pin  # GPIO8
GP8: microcontroller.Pin  # GPIO8
SCK: microcontroller.Pin  # GPIO10
GP10: microcontroller.Pin  # GPIO10
MOSI: microcontroller.Pin  # GPIO11
GP11: microcontroller.Pin  # GPIO11
MISO: microcontroller.Pin  # GPIO12
GP12: microcontroller.Pin  # GPIO12
CS: microcontroller.Pin  # GPIO13
GP13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP34: microcontroller.Pin  # GPIO34
GP35: microcontroller.Pin  # GPIO35
GP36: microcontroller.Pin  # GPIO36
GP37: microcontroller.Pin  # GPIO37
GP38: microcontroller.Pin  # GPIO38
GP39: microcontroller.Pin  # GPIO39
SDA: microcontroller.Pin  # GPIO40
GP40: microcontroller.Pin  # GPIO40
SCL: microcontroller.Pin  # GPIO41
GP41: microcontroller.Pin  # GPIO41
GP42: microcontroller.Pin  # GPIO42
TX: microcontroller.Pin  # GPIO43
GP43: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
GP44: microcontroller.Pin  # GPIO44
LCD_MOSI: microcontroller.Pin  # GPIO11
LCD_CLK: microcontroller.Pin  # GPIO10
LCD_CS: microcontroller.Pin  # GPIO9
LCD_RST: microcontroller.Pin  # GPIO21
LCD_BACKLIGHT: microcontroller.Pin  # GPIO45
LCD_DC: microcontroller.Pin  # GPIO18


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
