# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32-S3-USB-OTG-N8
 - port: espressif
 - board_id: espressif_esp32s3_usb_otg_n8
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
USB_SEL: microcontroller.Pin  # GPIO18
LED_GREEN: microcontroller.Pin  # GPIO15
LED: microcontroller.Pin  # GPIO15
LED_YELLOW: microcontroller.Pin  # GPIO16
BUTTON_OK: microcontroller.Pin  # GPIO0
BUTTON_UP: microcontroller.Pin  # GPIO10
BUTTON_DW: microcontroller.Pin  # GPIO11
BUTTON_DOWN: microcontroller.Pin  # GPIO11
BUTTON_MENU: microcontroller.Pin  # GPIO14
LCD_RST: microcontroller.Pin  # GPIO8
LCD_EN: microcontroller.Pin  # GPIO5
LCD_DC: microcontroller.Pin  # GPIO4
LCD_SCLK: microcontroller.Pin  # GPIO6
LCD_SDA: microcontroller.Pin  # GPIO7
LCD_BL: microcontroller.Pin  # GPIO9
SD_SCK: microcontroller.Pin  # GPIO36
SD_D0: microcontroller.Pin  # GPIO37
SD_D1: microcontroller.Pin  # GPIO38
SD_D2: microcontroller.Pin  # GPIO33
SD_D3: microcontroller.Pin  # GPIO34
HOST_VOL: microcontroller.Pin  # GPIO1
BAT_VOL: microcontroller.Pin  # GPIO2
BATTERY: microcontroller.Pin  # GPIO2
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO2
LIMIT_EN: microcontroller.Pin  # GPIO17
OVER_CURRENT: microcontroller.Pin  # GPIO21
DEV_VBUS_EN: microcontroller.Pin  # GPIO12
BOOST_EN: microcontroller.Pin  # GPIO13
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44


# Members:
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
