# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Heltec Vison Master E290
 - port: espressif
 - board_id: heltec_vision_master_e290
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON0: microcontroller.Pin  # GPIO0
BUTTON1: microcontroller.Pin  # GPIO21
LED0: microcontroller.Pin  # GPIO45
ADC_CTRL: microcontroller.Pin  # GPIO46
ADC_IN: microcontroller.Pin  # GPIO7
BATTERY: microcontroller.Pin  # GPIO7
VEXT_CTRL: microcontroller.Pin  # GPIO18
LORA_CS: microcontroller.Pin  # GPIO8
LORA_SCK: microcontroller.Pin  # GPIO9
LORA_MOSI: microcontroller.Pin  # GPIO10
LORA_MISO: microcontroller.Pin  # GPIO11
LORA_RESET: microcontroller.Pin  # GPIO12
LORA_BUSY: microcontroller.Pin  # GPIO13
LORA_DIO1: microcontroller.Pin  # GPIO14
EPD_MOSI: microcontroller.Pin  # GPIO1
EPD_SCK: microcontroller.Pin  # GPIO2
EPD_CS: microcontroller.Pin  # GPIO3
EPD_DC: microcontroller.Pin  # GPIO4
EPD_RESET: microcontroller.Pin  # GPIO5
EPD_BUSY: microcontroller.Pin  # GPIO6
SDA: microcontroller.Pin  # GPIO38
SCL: microcontroller.Pin  # GPIO39
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
IO0: microcontroller.Pin  # GPIO0
IO17: microcontroller.Pin  # GPIO17
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
IO45: microcontroller.Pin  # GPIO45
IO47: microcontroller.Pin  # GPIO47
IO48: microcontroller.Pin  # GPIO48


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
