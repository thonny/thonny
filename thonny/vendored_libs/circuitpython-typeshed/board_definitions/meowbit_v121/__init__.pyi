# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for MEOWBIT
 - port: stm
 - board_id: meowbit_v121
 - NVM size: Unknown
 - Included modules: _asyncio, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, analogio, array, atexit, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, select, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, usb_cdc, usb_hid, usb_midi, vectorio, warnings
 - Frozen libraries: stage, ugame
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
LED_RED: microcontroller.Pin  # PB04
LED_GREEN: microcontroller.Pin  # PB05
DISP_SCK: microcontroller.Pin  # PB13
DISP_MISO: microcontroller.Pin  # PB14
DISP_MOSI: microcontroller.Pin  # PB15
DISP_CS: microcontroller.Pin  # PB12
DISP_DC: microcontroller.Pin  # PA08
DISP_RST: microcontroller.Pin  # PB10
DISP_BL: microcontroller.Pin  # PB03
BTNA: microcontroller.Pin  # PB09
BTNB: microcontroller.Pin  # PC03
RIGHT: microcontroller.Pin  # PB02
DOWN: microcontroller.Pin  # PA05
LEFT: microcontroller.Pin  # PA07
TEMP: microcontroller.Pin  # PC05
UP: microcontroller.Pin  # PA06
LIGHT: microcontroller.Pin  # PC02
MENU: microcontroller.Pin  # PC15
JACK_TX: microcontroller.Pin  # PA09
JACK_PWREN: microcontroller.Pin  # PA07
JACK_SND: microcontroller.Pin  # PB08
ACC_INT: microcontroller.Pin  # PC14
ACC_SCL: microcontroller.Pin  # PB06
ACC_SDA: microcontroller.Pin  # PB07
SDA: microcontroller.Pin  # PB07
SCL: microcontroller.Pin  # PB06
NSS: microcontroller.Pin  # PA15
MOSI: microcontroller.Pin  # PC12
MISO: microcontroller.Pin  # PC11
SCK: microcontroller.Pin  # PC10
P20: microcontroller.Pin  # PB07
P19: microcontroller.Pin  # PB06
P16: microcontroller.Pin  # PA15
P15: microcontroller.Pin  # PC12
P14: microcontroller.Pin  # PC11
P13: microcontroller.Pin  # PC10
P2: microcontroller.Pin  # PA02
P12: microcontroller.Pin  # PA03
P11: microcontroller.Pin  # PB03
P10: microcontroller.Pin  # PC00
P9: microcontroller.Pin  # PC06
P8: microcontroller.Pin  # PA04
P1: microcontroller.Pin  # PA01
P7: microcontroller.Pin  # PA10
P6: microcontroller.Pin  # PC07
P5: microcontroller.Pin  # PB05
P4: microcontroller.Pin  # PC01
P0: microcontroller.Pin  # PA00
P3: microcontroller.Pin  # PB00


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#     { MP_ROM_QSTR(MP_QSTR_INTERNAL_SPI), MP_ROM_PTR(&supervisor_flash_spi_bus) },
