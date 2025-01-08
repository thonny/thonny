# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Espruino Bangle.js 2
 - port: nordic
 - board_id: espruino_banglejs2
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, alarm, analogio, array, atexit, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, nvm, os, os.getenv, paralleldisplaybus, pulseio, pwmio, random, re, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
PRESSURE_SCL: microcontroller.Pin  # P0_02
VOLTAGE_MONITOR: microcontroller.Pin  # P0_03
MEMLCD_CS: microcontroller.Pin  # P0_05
MEMLCD_EXTCOMIN: microcontroller.Pin  # P0_06
MEMLCD_DISP: microcontroller.Pin  # P0_07
BACKLIGHT: microcontroller.Pin  # P0_08
BUTTON: microcontroller.Pin  # P0_17
VIBRATE: microcontroller.Pin  # P0_19
HRM_POWER: microcontroller.Pin  # P0_21
HRM_INT: microcontroller.Pin  # P0_22
CHARGE_PORT: microcontroller.Pin  # P0_23
HRM_SDA: microcontroller.Pin  # P0_24
CHARGE_COMPLETE: microcontroller.Pin  # P0_25
MEMLCD_SCK: microcontroller.Pin  # P0_26
MEMLCD_MOSI: microcontroller.Pin  # P0_27
GPS_POWER: microcontroller.Pin  # P0_29
GPS_TX: microcontroller.Pin  # P0_30
GPS_RX: microcontroller.Pin  # P0_31
HRM_SCL: microcontroller.Pin  # P1_00
TOUCH_SDA: microcontroller.Pin  # P1_01
TOUCH_SCL: microcontroller.Pin  # P1_02
TOUCH_INT: microcontroller.Pin  # P1_03
ACCEL_SDA: microcontroller.Pin  # P1_04
ACCEL_SCL: microcontroller.Pin  # P1_05
COMPASS_SDA: microcontroller.Pin  # P1_10
COMPASS_SCL: microcontroller.Pin  # P1_11
PRESSURE_SDA: microcontroller.Pin  # P1_13


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
