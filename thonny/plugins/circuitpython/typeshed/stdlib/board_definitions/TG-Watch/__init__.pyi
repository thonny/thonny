# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for TG-Watch
 - port: nordic
 - board_id: TG-Watch
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_ble, adafruit_ble_apple_notification_center, adafruit_display_shapes, adafruit_display_text, adafruit_drv2605, adafruit_ds3231, adafruit_focaltouch, adafruit_lc709203f, adafruit_lsm6ds, adafruit_progressbar, adafruit_register, adafruit_st7789
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SCK: microcontroller.Pin  # P0_14
MOSI: microcontroller.Pin  # P0_13
MISO: microcontroller.Pin  # P0_15
TX: microcontroller.Pin  # P0_25
RX: microcontroller.Pin  # P0_24
SCL: microcontroller.Pin  # P0_11
SDA: microcontroller.Pin  # P0_12
VBUS_PRESENT: microcontroller.Pin  # P1_04
HAPTIC_ENABLE: microcontroller.Pin  # P1_06
HAPTIC_INT: microcontroller.Pin  # P1_07
CTP_INT: microcontroller.Pin  # P1_05
CTP_RST: microcontroller.Pin  # P1_03
TFT_RST: microcontroller.Pin  # P1_01
TFT_DC: microcontroller.Pin  # P1_12
D21: microcontroller.Pin  # P1_13
TFT_CS: microcontroller.Pin  # P1_14
ACCEL_INT1: microcontroller.Pin  # P1_11
ACCEL_INT2: microcontroller.Pin  # P1_10
BATTERY_DIV: microcontroller.Pin  # P0_29
RTC_INT: microcontroller.Pin  # P0_27
RTC_RST: microcontroller.Pin  # P0_26
CHRG_STAT: microcontroller.Pin  # P0_06
BACKLIGHT: microcontroller.Pin  # P0_07
BAT_INT: microcontroller.Pin  # P0_08
SMC_RST: microcontroller.Pin  # P0_04
_A0: microcontroller.Pin  # P0_04
_A1: microcontroller.Pin  # P0_05
_A2: microcontroller.Pin  # P0_30
_A3: microcontroller.Pin  # P0_28
_A4: microcontroller.Pin  # P0_02
_A5: microcontroller.Pin  # P0_03
AREF: microcontroller.Pin  # P0_31
_VOLTAGE_MONITOR: microcontroller.Pin  # P0_29
_BATTERY: microcontroller.Pin  # P0_29
_SWITCH: microcontroller.Pin  # P1_02
_NFC1: microcontroller.Pin  # P0_09
_NFC2: microcontroller.Pin  # P0_10
_D2: microcontroller.Pin  # P0_10
_D5: microcontroller.Pin  # P1_08
_D6: microcontroller.Pin  # P0_07
_D9: microcontroller.Pin  # P0_26
_D10: microcontroller.Pin  # P0_27
_D11: microcontroller.Pin  # P0_06
_D12: microcontroller.Pin  # P0_08
_D13: microcontroller.Pin  # P1_09
_NEOPIXEL: microcontroller.Pin  # P0_16


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
