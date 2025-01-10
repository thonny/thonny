# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Servo 2040
 - port: raspberrypi
 - board_id: pimoroni_servo2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SERVO_1: microcontroller.Pin  # GPIO0
SERVO_2: microcontroller.Pin  # GPIO1
SERVO_3: microcontroller.Pin  # GPIO2
SERVO_4: microcontroller.Pin  # GPIO3
SERVO_5: microcontroller.Pin  # GPIO4
SERVO_6: microcontroller.Pin  # GPIO5
SERVO_7: microcontroller.Pin  # GPIO6
SERVO_8: microcontroller.Pin  # GPIO7
SERVO_9: microcontroller.Pin  # GPIO8
SERVO_10: microcontroller.Pin  # GPIO9
SERVO_11: microcontroller.Pin  # GPIO10
SERVO_12: microcontroller.Pin  # GPIO11
SERVO_13: microcontroller.Pin  # GPIO12
SERVO_14: microcontroller.Pin  # GPIO13
SERVO_15: microcontroller.Pin  # GPIO14
SERVO_16: microcontroller.Pin  # GPIO15
SERVO_17: microcontroller.Pin  # GPIO16
SERVO_18: microcontroller.Pin  # GPIO17
NEOPIXEL: microcontroller.Pin  # GPIO18
LED_DATA: microcontroller.Pin  # GPIO18
INT: microcontroller.Pin  # GPIO19
GP19: microcontroller.Pin  # GPIO19
SDA: microcontroller.Pin  # GPIO20
GP20: microcontroller.Pin  # GPIO20
SCL: microcontroller.Pin  # GPIO21
GP21: microcontroller.Pin  # GPIO21
USER_SW: microcontroller.Pin  # GPIO23
ADC_ADDR_0: microcontroller.Pin  # GPIO22
ADC_ADDR_1: microcontroller.Pin  # GPIO24
ADC_ADDR_2: microcontroller.Pin  # GPIO25
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
SHARED_ADC: microcontroller.Pin  # GPIO29


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none