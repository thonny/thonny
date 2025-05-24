# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO T-Dongle S3
 - port: espressif
 - board_id: lilygo_tdongle_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO12: microcontroller.Pin  # GPIO12
IO14: microcontroller.Pin  # GPIO14
IO16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO21: microcontroller.Pin  # GPIO21
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
BUTTON0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
STEMMA_SDA: microcontroller.Pin  # GPIO43
STEMMA_SCL: microcontroller.Pin  # GPIO44
LCD_DC: microcontroller.Pin  # GPIO2
LCD_CS: microcontroller.Pin  # GPIO4
LCD_CLK: microcontroller.Pin  # GPIO5
LCD_DIN: microcontroller.Pin  # GPIO3
LCD_RST: microcontroller.Pin  # GPIO1
LCD_BCKL: microcontroller.Pin  # GPIO38
APA102_CLK: microcontroller.Pin  # GPIO39
APA102_DI: microcontroller.Pin  # GPIO40
SD_D0: microcontroller.Pin  # GPIO14
SD_D1: microcontroller.Pin  # GPIO17
SD_D2: microcontroller.Pin  # GPIO21
SD_D3: microcontroller.Pin  # GPIO18
SD_SCK: microcontroller.Pin  # GPIO12
SD_CMD: microcontroller.Pin  # GPIO16


# Members:
def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
