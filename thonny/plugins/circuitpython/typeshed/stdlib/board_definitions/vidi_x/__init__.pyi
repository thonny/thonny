# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for VIDI X V1.1
 - port: espressif
 - board_id: vidi_x
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
VOLUME: microcontroller.Pin  # GPIO0
EXP9: microcontroller.Pin  # GPIO0
GPIO0: microcontroller.Pin  # GPIO0
TX: microcontroller.Pin  # GPIO1
EXP16: microcontroller.Pin  # GPIO1
GPIO1: microcontroller.Pin  # GPIO1
STATUS: microcontroller.Pin  # GPIO2
EXP8: microcontroller.Pin  # GPIO2
GPIO2: microcontroller.Pin  # GPIO2
RX: microcontroller.Pin  # GPIO3
EXP14: microcontroller.Pin  # GPIO3
GPIO3: microcontroller.Pin  # GPIO3
VSPI_CS2: microcontroller.Pin  # GPIO4
EXP10: microcontroller.Pin  # GPIO4
TOUCH_CS: microcontroller.Pin  # GPIO4
GPIO4: microcontroller.Pin  # GPIO4
VSPI_CS0: microcontroller.Pin  # GPIO5
EXP11: microcontroller.Pin  # GPIO5
LCD_CS: microcontroller.Pin  # GPIO5
GPIO5: microcontroller.Pin  # GPIO5
TOUCH_IRQ: microcontroller.Pin  # GPIO12
EXP20: microcontroller.Pin  # GPIO12
GPIO12: microcontroller.Pin  # GPIO12
MENU: microcontroller.Pin  # GPIO13
EXP17: microcontroller.Pin  # GPIO13
GPIO13: microcontroller.Pin  # GPIO13
MIC: microcontroller.Pin  # GPIO14
EXP19: microcontroller.Pin  # GPIO14
GPIO14: microcontroller.Pin  # GPIO14
IRTX: microcontroller.Pin  # GPIO15
EXP7: microcontroller.Pin  # GPIO15
GPIO15: microcontroller.Pin  # GPIO15
VSPI_SCK: microcontroller.Pin  # GPIO18
EXP12: microcontroller.Pin  # GPIO18
TOUCH_SCK: microcontroller.Pin  # GPIO18
LCD_SCK: microcontroller.Pin  # GPIO18
SD_SCK: microcontroller.Pin  # GPIO18
GPIO18: microcontroller.Pin  # GPIO18
VSPI_MISO: microcontroller.Pin  # GPIO19
EXP13: microcontroller.Pin  # GPIO19
TOUCH_MISO: microcontroller.Pin  # GPIO19
LCD_MISO: microcontroller.Pin  # GPIO19
SD_MISO: microcontroller.Pin  # GPIO19
GPIO19: microcontroller.Pin  # GPIO19
LCD_DC: microcontroller.Pin  # GPIO21
EXP15: microcontroller.Pin  # GPIO21
GPIO21: microcontroller.Pin  # GPIO21
VSPI_CS1: microcontroller.Pin  # GPIO22
EXP18: microcontroller.Pin  # GPIO22
SD_CS: microcontroller.Pin  # GPIO22
GPIO22: microcontroller.Pin  # GPIO22
VSPI_MOSI: microcontroller.Pin  # GPIO23
EXP28: microcontroller.Pin  # GPIO23
GPIO23: microcontroller.Pin  # GPIO23
TOUCH_MOSI: microcontroller.Pin  # GPIO19
LCD_MOSI: microcontroller.Pin  # GPIO19
SD_MOSI: microcontroller.Pin  # GPIO19
GPIO19: microcontroller.Pin  # GPIO19
IRRX: microcontroller.Pin  # GPIO25
SPEAKER_IN: microcontroller.Pin  # GPIO25
GPIO25: microcontroller.Pin  # GPIO25
TEMP: microcontroller.Pin  # GPIO26
RGB_LED: microcontroller.Pin  # GPIO26
GPIO26: microcontroller.Pin  # GPIO26
SELECT: microcontroller.Pin  # GPIO27
EXP22: microcontroller.Pin  # GPIO27
GPIO27: microcontroller.Pin  # GPIO27
BTN_A: microcontroller.Pin  # GPIO32
EXP23: microcontroller.Pin  # GPIO32
GPIO32: microcontroller.Pin  # GPIO32
BTN_B: microcontroller.Pin  # GPIO33
EXP21: microcontroller.Pin  # GPIO33
GPIO33: microcontroller.Pin  # GPIO33
BTN_L_R: microcontroller.Pin  # GPIO34
EXP25: microcontroller.Pin  # GPIO34
GPIO34: microcontroller.Pin  # GPIO34
BTN_UP_DOWN: microcontroller.Pin  # GPIO35
EXP24: microcontroller.Pin  # GPIO35
GPIO35: microcontroller.Pin  # GPIO35
ADC_BAT: microcontroller.Pin  # GPIO36
EXP27: microcontroller.Pin  # GPIO36
GPIO36: microcontroller.Pin  # GPIO36
START: microcontroller.Pin  # GPIO39
EXP26: microcontroller.Pin  # GPIO39
GPIO39: microcontroller.Pin  # GPIO39


# Members:
def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def VIDIIC() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
