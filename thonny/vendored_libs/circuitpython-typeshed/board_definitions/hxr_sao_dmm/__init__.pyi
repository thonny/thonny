# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for HXR.DK SAO Digital Multimeter
 - port: raspberrypi
 - board_id: hxr_sao_dmm
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_bitmap_font, adafruit_display_shapes, adafruit_display_text, adafruit_displayio_ssd1306, test
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
UART_TX: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
UART_RX: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
SAO_SDA: microcontroller.Pin  # GPIO4
SDA0: microcontroller.Pin  # GPIO4
GP4: microcontroller.Pin  # GPIO4
SAO_SCL: microcontroller.Pin  # GPIO5
SCL0: microcontroller.Pin  # GPIO5
GP5: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
DISPLAY_SDA: microcontroller.Pin  # GPIO14
SDA1: microcontroller.Pin  # GPIO14
SDA: microcontroller.Pin  # GPIO14
GP14: microcontroller.Pin  # GPIO14
DISPLAY_SCL: microcontroller.Pin  # GPIO15
SCL1: microcontroller.Pin  # GPIO15
SCL: microcontroller.Pin  # GPIO15
GP15: microcontroller.Pin  # GPIO15
ENC_A: microcontroller.Pin  # GPIO16
GP16: microcontroller.Pin  # GPIO16
ENC_B: microcontroller.Pin  # GPIO17
GP17: microcontroller.Pin  # GPIO17
BUTTON_FN: microcontroller.Pin  # GPIO18
BUTTON: microcontroller.Pin  # GPIO18
GP18: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
BUZZER_A: microcontroller.Pin  # GPIO22
PWM3_A: microcontroller.Pin  # GPIO22
GP22: microcontroller.Pin  # GPIO22
BUZZER_B: microcontroller.Pin  # GPIO23
PWM3_B: microcontroller.Pin  # GPIO23
GP23: microcontroller.Pin  # GPIO23
GP24: microcontroller.Pin  # GPIO24
GP25: microcontroller.Pin  # GPIO25
SAO_GPIO1: microcontroller.Pin  # GPIO26
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
SAO_GPIO2: microcontroller.Pin  # GPIO27
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
MEASURE_RES: microcontroller.Pin  # GPIO28
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
MEASURE_VIN: microcontroller.Pin  # GPIO29
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29
GP29_A3: microcontroller.Pin  # GPIO29
GP29: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def DISPLAY_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
