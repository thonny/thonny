# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for HEIA-FR Picomo V2
 - port: raspberrypi
 - board_id: heiafr_picomo_v2
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_display_shapes, adafruit_display_text, adafruit_progressbar, adafruit_register, adafruit_st7789
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
GP2: microcontroller.Pin  # GPIO2
SW_UP: microcontroller.Pin  # GPIO3
S1: microcontroller.Pin  # GPIO3
GP3: microcontroller.Pin  # GPIO3
SW_MID: microcontroller.Pin  # GPIO4
S5: microcontroller.Pin  # GPIO4
GP4: microcontroller.Pin  # GPIO4
SW_DOWN: microcontroller.Pin  # GPIO5
S2: microcontroller.Pin  # GPIO5
GP5: microcontroller.Pin  # GPIO5
SW_TOPR: microcontroller.Pin  # GPIO6
BOOTSEL: microcontroller.Pin  # GPIO6
S7: microcontroller.Pin  # GPIO6
GP6: microcontroller.Pin  # GPIO6
SW_RIGHT: microcontroller.Pin  # GPIO7
S4: microcontroller.Pin  # GPIO7
GP7: microcontroller.Pin  # GPIO7
LED_B: microcontroller.Pin  # GPIO8
GP8: microcontroller.Pin  # GPIO8
LED_G: microcontroller.Pin  # GPIO9
GP9: microcontroller.Pin  # GPIO9
LED_R: microcontroller.Pin  # GPIO10
GP10: microcontroller.Pin  # GPIO10
BUZZER: microcontroller.Pin  # GPIO11
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
DISP_DC: microcontroller.Pin  # GPIO16
GP16: microcontroller.Pin  # GPIO16
DISP_CS: microcontroller.Pin  # GPIO17
GP17: microcontroller.Pin  # GPIO17
DISP_SCL: microcontroller.Pin  # GPIO18
GP18: microcontroller.Pin  # GPIO18
DISP_SDA: microcontroller.Pin  # GPIO19
GP19: microcontroller.Pin  # GPIO19
TEMP_SDA: microcontroller.Pin  # GPIO20
GP20: microcontroller.Pin  # GPIO20
TEMP_SCL: microcontroller.Pin  # GPIO21
GP21: microcontroller.Pin  # GPIO21
SW_LEFT: microcontroller.Pin  # GPIO22
S3: microcontroller.Pin  # GPIO22
GP22: microcontroller.Pin  # GPIO22
SW_TOPL: microcontroller.Pin  # GPIO23
S6: microcontroller.Pin  # GPIO23
GP23: microcontroller.Pin  # GPIO23
USB_OVCUR: microcontroller.Pin  # GPIO24
GP24: microcontroller.Pin  # GPIO24
GP25: microcontroller.Pin  # GPIO25
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
