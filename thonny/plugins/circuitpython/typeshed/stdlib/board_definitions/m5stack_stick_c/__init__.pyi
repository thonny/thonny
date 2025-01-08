# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Stick C
 - port: espressif
 - board_id: m5stack_stick_c
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
A26: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
A36: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
A0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
PORTA_SDA: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
PORTA_SCL: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
LED: microcontroller.Pin  # GPIO10
IR_LED: microcontroller.Pin  # GPIO9
BTN_A: microcontroller.Pin  # GPIO37
BTN_B: microcontroller.Pin  # GPIO39
SYS_SDA: microcontroller.Pin  # GPIO21
SYS_SCL: microcontroller.Pin  # GPIO22
SYS_INT: microcontroller.Pin  # GPIO35
PMU_N_VBUSEN: microcontroller.Pin  # GPIO27
PDM_MIC_CLK: microcontroller.Pin  # GPIO0
PDM_MIC_DATA: microcontroller.Pin  # GPIO34
LCD_MOSI: microcontroller.Pin  # GPIO15
LCD_CLK: microcontroller.Pin  # GPIO13
LCD_DC: microcontroller.Pin  # GPIO23
LCD_RST: microcontroller.Pin  # GPIO18
LCD_CS: microcontroller.Pin  # GPIO5


# Members:
def SYS_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
