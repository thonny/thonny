# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Cardputer
 - port: espressif
 - board_id: m5stack_cardputer
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO1
PORTA1: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
G1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO2
PORTA2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
G2: microcontroller.Pin  # GPIO2
KB_COL_0: microcontroller.Pin  # GPIO13
KB_COL_1: microcontroller.Pin  # GPIO15
KB_COL_2: microcontroller.Pin  # GPIO3
KB_COL_3: microcontroller.Pin  # GPIO4
KB_COL_4: microcontroller.Pin  # GPIO5
KB_COL_5: microcontroller.Pin  # GPIO6
KB_COL_6: microcontroller.Pin  # GPIO7
KB_A_0: microcontroller.Pin  # GPIO8
KB_A_1: microcontroller.Pin  # GPIO9
KB_A_2: microcontroller.Pin  # GPIO11
NEOPIXEL: microcontroller.Pin  # GPIO21
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO41
I2S_DATA: microcontroller.Pin  # GPIO42
I2S_WORD_SELECT: microcontroller.Pin  # GPIO43
MIC_DATA: microcontroller.Pin  # GPIO46
MIC_CLK: microcontroller.Pin  # GPIO43
IR_TX: microcontroller.Pin  # GPIO44
SD_MOSI: microcontroller.Pin  # GPIO14
SD_SCK: microcontroller.Pin  # GPIO40
SD_MISO: microcontroller.Pin  # GPIO39
SD_CS: microcontroller.Pin  # GPIO12
TFT_RST: microcontroller.Pin  # GPIO33
TFT_RESET: microcontroller.Pin  # GPIO33
TFT_DC: microcontroller.Pin  # GPIO34
TFT_RS: microcontroller.Pin  # GPIO34
TFT_MOSI: microcontroller.Pin  # GPIO35
TFT_DATA: microcontroller.Pin  # GPIO35
TFT_SCK: microcontroller.Pin  # GPIO36
TFT_CS: microcontroller.Pin  # GPIO37
TFT_BACKLIGHT: microcontroller.Pin  # GPIO38
TFT_BL: microcontroller.Pin  # GPIO38
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
BAT_ADC: microcontroller.Pin  # GPIO10


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def PORTA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def TFT_SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
