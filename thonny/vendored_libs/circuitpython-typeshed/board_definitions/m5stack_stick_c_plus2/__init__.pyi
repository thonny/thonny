# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Stick C Plus2
 - port: espressif
 - board_id: m5stack_stick_c_plus2
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
G26: microcontroller.Pin  # GPIO26
G36: microcontroller.Pin  # GPIO36
G25: microcontroller.Pin  # GPIO25
G0: microcontroller.Pin  # GPIO0
G32: microcontroller.Pin  # GPIO32
GROVE_SDA: microcontroller.Pin  # GPIO32
G33: microcontroller.Pin  # GPIO33
GROVE_SCL: microcontroller.Pin  # GPIO33
G37: microcontroller.Pin  # GPIO37
BTN_A: microcontroller.Pin  # GPIO37
G39: microcontroller.Pin  # GPIO39
BTN_B: microcontroller.Pin  # GPIO39
G35: microcontroller.Pin  # GPIO35
BTN_C: microcontroller.Pin  # GPIO35
BTN_PWR: microcontroller.Pin  # GPIO35
G2: microcontroller.Pin  # GPIO2
SPEAKER: microcontroller.Pin  # GPIO2
G19: microcontroller.Pin  # GPIO19
IR_LED: microcontroller.Pin  # GPIO19
LED: microcontroller.Pin  # GPIO19
LCD_MOSI: microcontroller.Pin  # GPIO15
LCD_CLK: microcontroller.Pin  # GPIO13
LCD_DC: microcontroller.Pin  # GPIO14
LCD_RST: microcontroller.Pin  # GPIO12
LCD_CS: microcontroller.Pin  # GPIO5
LCD_BL: microcontroller.Pin  # GPIO27
G38: microcontroller.Pin  # GPIO38
BAT_ADC: microcontroller.Pin  # GPIO38
PDM_MIC_CLK: microcontroller.Pin  # GPIO0
G34: microcontroller.Pin  # GPIO34
PDM_MIC_DATA: microcontroller.Pin  # GPIO34
G21: microcontroller.Pin  # GPIO21
SYS_SDA: microcontroller.Pin  # GPIO21
G22: microcontroller.Pin  # GPIO22
SYS_SCL: microcontroller.Pin  # GPIO22
WAKE: microcontroller.Pin  # GPIO35
G4: microcontroller.Pin  # GPIO4
HOLD: microcontroller.Pin  # GPIO4


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
