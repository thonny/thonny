# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Bradán Lane STUDIO Explorer Badge
 - port: raspberrypi
 - board_id: bradanlanestudio_explorer_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_bitmap_font, adafruit_display_shapes, adafruit_display_text, adafruit_hid, adafruit_irremote, adafruit_ticks, asyncio, neopixel, test
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO0
GP1: microcontroller.Pin  # GPIO1
IR_TX: microcontroller.Pin  # GPIO0
IR_RX: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO2
SCL: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
LED: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
NEOPIXEL: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
SPEAKER: microcontroller.Pin  # GPIO6
SPEAKER_EN: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
DISPLAY_EN: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
SPI_BUSY: microcontroller.Pin  # GPIO9
SPI_RESET: microcontroller.Pin  # GPIO10
SPI_DC: microcontroller.Pin  # GPIO11
SPI_MISO: microcontroller.Pin  # GPIO12
SPI_CS: microcontroller.Pin  # GPIO13
SPI_SCK: microcontroller.Pin  # GPIO14
SPI_MOSI: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
I2S_DATA: microcontroller.Pin  # GPIO16
I2S_BCK: microcontroller.Pin  # GPIO17
I2S_LRCK: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
GP22: microcontroller.Pin  # GPIO22
GP23: microcontroller.Pin  # GPIO23
GP24: microcontroller.Pin  # GPIO24
GP25: microcontroller.Pin  # GPIO25
GP26: microcontroller.Pin  # GPIO26
GP27: microcontroller.Pin  # GPIO27
TOUCH1: microcontroller.Pin  # GPIO19
TOUCH2: microcontroller.Pin  # GPIO20
TOUCH3: microcontroller.Pin  # GPIO21
TOUCH4: microcontroller.Pin  # GPIO22
TOUCH5: microcontroller.Pin  # GPIO23
TOUCH6: microcontroller.Pin  # GPIO24
TOUCH7: microcontroller.Pin  # GPIO25
TOUCH8: microcontroller.Pin  # GPIO26
TOUCH9: microcontroller.Pin  # GPIO27
GP28: microcontroller.Pin  # GPIO28
GP29: microcontroller.Pin  # GPIO29


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
