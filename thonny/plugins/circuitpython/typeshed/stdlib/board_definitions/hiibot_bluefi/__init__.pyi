# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for HiiBot BlueFi
 - port: nordic
 - board_id: hiibot_bluefi
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
P0: microcontroller.Pin  # P0_28
D0: microcontroller.Pin  # P0_28
A0: microcontroller.Pin  # P0_28
RX: microcontroller.Pin  # P0_28
P1: microcontroller.Pin  # P0_02
D1: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_02
TX: microcontroller.Pin  # P0_02
P2: microcontroller.Pin  # P0_29
D2: microcontroller.Pin  # P0_29
A2: microcontroller.Pin  # P0_29
P3: microcontroller.Pin  # P0_30
D3: microcontroller.Pin  # P0_30
A3: microcontroller.Pin  # P0_30
P4: microcontroller.Pin  # P0_03
D4: microcontroller.Pin  # P0_03
A4: microcontroller.Pin  # P0_03
P5: microcontroller.Pin  # P1_07
D5: microcontroller.Pin  # P1_07
BUTTON_A: microcontroller.Pin  # P1_07
P6: microcontroller.Pin  # P0_08
D6: microcontroller.Pin  # P0_08
P7: microcontroller.Pin  # P0_25
D7: microcontroller.Pin  # P0_25
P8: microcontroller.Pin  # P0_23
D8: microcontroller.Pin  # P0_23
P9: microcontroller.Pin  # P0_21
D9: microcontroller.Pin  # P0_21
P10: microcontroller.Pin  # P0_19
D10: microcontroller.Pin  # P0_19
P11: microcontroller.Pin  # P1_09
D11: microcontroller.Pin  # P1_09
BUTTON_B: microcontroller.Pin  # P1_09
P12: microcontroller.Pin  # P0_16
D12: microcontroller.Pin  # P0_16
P13: microcontroller.Pin  # P0_06
D13: microcontroller.Pin  # P0_06
SCK: microcontroller.Pin  # P0_06
P14: microcontroller.Pin  # P0_04
D14: microcontroller.Pin  # P0_04
A5: microcontroller.Pin  # P0_04
MISO: microcontroller.Pin  # P0_04
P15: microcontroller.Pin  # P0_26
D15: microcontroller.Pin  # P0_26
MOSI: microcontroller.Pin  # P0_26
P16: microcontroller.Pin  # P0_01
D16: microcontroller.Pin  # P0_01
P17: microcontroller.Pin  # P1_12
D17: microcontroller.Pin  # P1_12
LED: microcontroller.Pin  # P1_12
REDLED: microcontroller.Pin  # P1_12
P18: microcontroller.Pin  # P1_10
D18: microcontroller.Pin  # P1_10
NEOPIXEL: microcontroller.Pin  # P1_10
P19: microcontroller.Pin  # P0_00
D19: microcontroller.Pin  # P0_00
SCL: microcontroller.Pin  # P0_00
P20: microcontroller.Pin  # P0_31
D20: microcontroller.Pin  # P0_31
A6: microcontroller.Pin  # P0_31
SDA: microcontroller.Pin  # P0_31
P21: microcontroller.Pin  # P0_09
D21: microcontroller.Pin  # P0_09
MICROPHONE_CLOCK: microcontroller.Pin  # P0_09
P22: microcontroller.Pin  # P0_10
D22: microcontroller.Pin  # P0_10
MICROPHONE_DATA: microcontroller.Pin  # P0_10
P23: microcontroller.Pin  # P0_07
D23: microcontroller.Pin  # P0_07
TFT_SCK: microcontroller.Pin  # P0_07
P24: microcontroller.Pin  # P1_08
D24: microcontroller.Pin  # P1_08
TFT_MOSI: microcontroller.Pin  # P1_08
P25: microcontroller.Pin  # P0_05
D25: microcontroller.Pin  # P0_05
TFT_CS: microcontroller.Pin  # P0_05
P26: microcontroller.Pin  # P0_27
D26: microcontroller.Pin  # P0_27
TFT_DC: microcontroller.Pin  # P0_27
P27: microcontroller.Pin  # P1_13
D27: microcontroller.Pin  # P1_13
TFT_BACKLIGHT: microcontroller.Pin  # P1_13
P34: microcontroller.Pin  # P0_22
D34: microcontroller.Pin  # P0_22
WIFI_SCK: microcontroller.Pin  # P0_22
P35: microcontroller.Pin  # P0_17
D35: microcontroller.Pin  # P0_17
WIFI_MISO: microcontroller.Pin  # P0_17
P36: microcontroller.Pin  # P0_20
D36: microcontroller.Pin  # P0_20
WIFI_MOSI: microcontroller.Pin  # P0_20
P37: microcontroller.Pin  # P0_15
D37: microcontroller.Pin  # P0_15
WIFI_BUSY: microcontroller.Pin  # P0_15
P38: microcontroller.Pin  # P0_24
D38: microcontroller.Pin  # P0_24
WIFI_CS: microcontroller.Pin  # P0_24
P39: microcontroller.Pin  # P1_00
D39: microcontroller.Pin  # P1_00
WIFI_RESET: microcontroller.Pin  # P1_00
P40: microcontroller.Pin  # P0_13
D40: microcontroller.Pin  # P0_13
WIFI_PWR: microcontroller.Pin  # P0_13
P41: microcontroller.Pin  # P0_11
D41: microcontroller.Pin  # P0_11
SENSORS_SCL: microcontroller.Pin  # P0_11
P42: microcontroller.Pin  # P0_12
D42: microcontroller.Pin  # P0_12
SENSORS_SDA: microcontroller.Pin  # P0_12
P43: microcontroller.Pin  # P0_14
D43: microcontroller.Pin  # P0_14
IMU_IRQ: microcontroller.Pin  # P0_14
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # P0_14
P44: microcontroller.Pin  # P1_14
D44: microcontroller.Pin  # P1_14
WHITELED: microcontroller.Pin  # P1_14
P45: microcontroller.Pin  # P1_11
D45: microcontroller.Pin  # P1_11
SPEAKER_ENABLE: microcontroller.Pin  # P1_11
P46: microcontroller.Pin  # P1_15
D46: microcontroller.Pin  # P1_15
SPEAKER: microcontroller.Pin  # P1_15
AUDIO: microcontroller.Pin  # P1_15


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
