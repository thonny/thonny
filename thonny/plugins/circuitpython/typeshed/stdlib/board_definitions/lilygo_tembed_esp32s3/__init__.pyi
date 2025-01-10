# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO TEMBED ESP32S3
 - port: espressif
 - board_id: lilygo_tembed_esp32s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
IO45: microcontroller.Pin  # GPIO45
IO46: microcontroller.Pin  # GPIO46
IO47: microcontroller.Pin  # GPIO47
IO48: microcontroller.Pin  # GPIO48
NEOPIXEL: microcontroller.Pin  # GPIO48
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
TFT_LITE: microcontroller.Pin  # GPIO15
TFT_MOSI: microcontroller.Pin  # GPIO11
TFT_SCK: microcontroller.Pin  # GPIO12
TFT_RST: microcontroller.Pin  # GPIO9
TFT_CS: microcontroller.Pin  # GPIO10
TFT_DC: microcontroller.Pin  # GPIO13
SD_CS: microcontroller.Pin  # GPIO39
SD_SCLK: microcontroller.Pin  # GPIO40
SD_MOSI: microcontroller.Pin  # GPIO41
SD_MISO: microcontroller.Pin  # GPIO38
ES_BCLK: microcontroller.Pin  # GPIO47
ES_LRCK: microcontroller.Pin  # GPIO21
ES_DIN: microcontroller.Pin  # GPIO14
ES_MCLK: microcontroller.Pin  # GPIO48
I2S_BCLK: microcontroller.Pin  # GPIO7
I2S_WCLK: microcontroller.Pin  # GPIO5
I2S_DOUT: microcontroller.Pin  # GPIO6
ENCODER_A: microcontroller.Pin  # GPIO2
ENCODER_B: microcontroller.Pin  # GPIO1
ENCODER_BUTTON: microcontroller.Pin  # GPIO0
APA102_CLK: microcontroller.Pin  # GPIO45
APA102_DI: microcontroller.Pin  # GPIO42


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none