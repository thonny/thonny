# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit CLUE nRF52840 Express
 - port: nordic
 - board_id: clue_nrf52840_express
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
P0: microcontroller.Pin  # P0_04
D0: microcontroller.Pin  # P0_04
A2: microcontroller.Pin  # P0_04
RX: microcontroller.Pin  # P0_04
P1: microcontroller.Pin  # P0_05
D1: microcontroller.Pin  # P0_05
A3: microcontroller.Pin  # P0_05
TX: microcontroller.Pin  # P0_05
P2: microcontroller.Pin  # P0_03
D2: microcontroller.Pin  # P0_03
A4: microcontroller.Pin  # P0_03
P3: microcontroller.Pin  # P0_28
D3: microcontroller.Pin  # P0_28
A5: microcontroller.Pin  # P0_28
P4: microcontroller.Pin  # P0_02
D4: microcontroller.Pin  # P0_02
A6: microcontroller.Pin  # P0_02
P5: microcontroller.Pin  # P1_02
D5: microcontroller.Pin  # P1_02
BUTTON_A: microcontroller.Pin  # P1_02
P6: microcontroller.Pin  # P1_09
D6: microcontroller.Pin  # P1_09
P7: microcontroller.Pin  # P0_07
D7: microcontroller.Pin  # P0_07
P8: microcontroller.Pin  # P1_07
D8: microcontroller.Pin  # P1_07
P9: microcontroller.Pin  # P0_27
D9: microcontroller.Pin  # P0_27
P10: microcontroller.Pin  # P0_30
D10: microcontroller.Pin  # P0_30
A7: microcontroller.Pin  # P0_30
P11: microcontroller.Pin  # P1_10
D11: microcontroller.Pin  # P1_10
BUTTON_B: microcontroller.Pin  # P1_10
P12: microcontroller.Pin  # P0_31
D12: microcontroller.Pin  # P0_31
A0: microcontroller.Pin  # P0_31
P13: microcontroller.Pin  # P0_08
D13: microcontroller.Pin  # P0_08
SCK: microcontroller.Pin  # P0_08
P14: microcontroller.Pin  # P0_06
D14: microcontroller.Pin  # P0_06
MISO: microcontroller.Pin  # P0_06
P15: microcontroller.Pin  # P0_26
D15: microcontroller.Pin  # P0_26
MOSI: microcontroller.Pin  # P0_26
P16: microcontroller.Pin  # P0_29
D16: microcontroller.Pin  # P0_29
A1: microcontroller.Pin  # P0_29
P17: microcontroller.Pin  # P1_01
D17: microcontroller.Pin  # P1_01
L: microcontroller.Pin  # P1_01
LED: microcontroller.Pin  # P1_01
P18: microcontroller.Pin  # P0_16
D18: microcontroller.Pin  # P0_16
NEOPIXEL: microcontroller.Pin  # P0_16
P19: microcontroller.Pin  # P0_25
D19: microcontroller.Pin  # P0_25
SCL: microcontroller.Pin  # P0_25
P20: microcontroller.Pin  # P0_24
D20: microcontroller.Pin  # P0_24
SDA: microcontroller.Pin  # P0_24
MICROPHONE_CLOCK: microcontroller.Pin  # P0_01
MICROPHONE_DATA: microcontroller.Pin  # P0_00
SPEAKER: microcontroller.Pin  # P1_00
PROXIMITY_LIGHT_INTERRUPT: microcontroller.Pin  # P0_09
ACCELEROMETER_GYRO_INTERRUPT: microcontroller.Pin  # P1_06
WHITE_LEDS: microcontroller.Pin  # P0_10
TFT_RESET: microcontroller.Pin  # P1_03
TFT_BACKLIGHT: microcontroller.Pin  # P1_05
TFT_CS: microcontroller.Pin  # P0_12
TFT_DC: microcontroller.Pin  # P0_13
TFT_SCK: microcontroller.Pin  # P0_14
TFT_MOSI: microcontroller.Pin  # P0_15


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

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
