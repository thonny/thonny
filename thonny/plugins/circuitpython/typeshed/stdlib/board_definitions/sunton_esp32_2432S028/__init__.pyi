# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for sunton_esp32_2432S028
 - port: espressif
 - board_id: sunton_esp32_2432S028
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
BOOT0: microcontroller.Pin  # GPIO0
BUTTON: microcontroller.Pin  # GPIO0
LED_GREEN: microcontroller.Pin  # GPIO16
LED_RED: microcontroller.Pin  # GPIO4
LED_BLUE: microcontroller.Pin  # GPIO17
LDR: microcontroller.Pin  # GPIO34
SPEAKER: microcontroller.Pin  # GPIO26
IO21: microcontroller.Pin  # GPIO21
IO22: microcontroller.Pin  # GPIO22
IO27: microcontroller.Pin  # GPIO27
IO35: microcontroller.Pin  # GPIO35
SDA: microcontroller.Pin  # GPIO27
SCL: microcontroller.Pin  # GPIO22
SD_MOSI: microcontroller.Pin  # GPIO23
SD_MISO: microcontroller.Pin  # GPIO19
SD_SCK: microcontroller.Pin  # GPIO18
SD_CS: microcontroller.Pin  # GPIO5
LCD_MOSI: microcontroller.Pin  # GPIO13
LCD_MISO: microcontroller.Pin  # GPIO12
LCD_SCK: microcontroller.Pin  # GPIO14
LCD_CS: microcontroller.Pin  # GPIO15
LCD_DC: microcontroller.Pin  # GPIO2
LCD_BCKL: microcontroller.Pin  # GPIO21
TOUCH_MOSI: microcontroller.Pin  # GPIO32
TOUCH_MISO: microcontroller.Pin  # GPIO39
TOUCH_SCK: microcontroller.Pin  # GPIO25
TOUCH_CS: microcontroller.Pin  # GPIO33
TOUCH_INT: microcontroller.Pin  # GPIO36


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
