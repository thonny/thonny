# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Motor 2040
 - port: raspberrypi
 - board_id: pimoroni_motor2040
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
MOTOR_A_P: microcontroller.Pin  # GPIO4
MOTOR_A_N: microcontroller.Pin  # GPIO5
MOTOR_B_P: microcontroller.Pin  # GPIO6
MOTOR_B_N: microcontroller.Pin  # GPIO7
MOTOR_C_P: microcontroller.Pin  # GPIO8
MOTOR_C_N: microcontroller.Pin  # GPIO9
MOTOR_D_P: microcontroller.Pin  # GPIO10
MOTOR_D_N: microcontroller.Pin  # GPIO11
ENCODER_A_A: microcontroller.Pin  # GPIO0
ENCODER_A_B: microcontroller.Pin  # GPIO1
ENCODER_B_A: microcontroller.Pin  # GPIO2
ENCODER_B_B: microcontroller.Pin  # GPIO3
ENCODER_C_A: microcontroller.Pin  # GPIO12
ENCODER_C_B: microcontroller.Pin  # GPIO13
ENCODER_D_A: microcontroller.Pin  # GPIO14
ENCODER_D_B: microcontroller.Pin  # GPIO15
TX: microcontroller.Pin  # GPIO16
TRIG: microcontroller.Pin  # GPIO16
RX: microcontroller.Pin  # GPIO17
ECHO: microcontroller.Pin  # GPIO17
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

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
