# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Heltec ESP32-S3-WIFI-LoRa-V3
 - port: espressif
 - board_id: heltec_esp32s3_wifi_lora_v3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_display_shapes, adafruit_display_text
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
GPIO7: microcontroller.Pin  # GPIO7
GPIO6: microcontroller.Pin  # GPIO6
GPIO5: microcontroller.Pin  # GPIO5
GPIO4: microcontroller.Pin  # GPIO4
GPIO3: microcontroller.Pin  # GPIO3
GPIO2: microcontroller.Pin  # GPIO2
GPIO1: microcontroller.Pin  # GPIO1
GPIO38: microcontroller.Pin  # GPIO38
GPIO39: microcontroller.Pin  # GPIO39
GPIO40: microcontroller.Pin  # GPIO40
GPIO41: microcontroller.Pin  # GPIO41
GPIO42: microcontroller.Pin  # GPIO42
GPIO43: microcontroller.Pin  # GPIO43
GPIO44: microcontroller.Pin  # GPIO44
GPIO45: microcontroller.Pin  # GPIO45
GPIO46: microcontroller.Pin  # GPIO46
GPIO37: microcontroller.Pin  # GPIO37
GPIO19: microcontroller.Pin  # GPIO19
GPIO20: microcontroller.Pin  # GPIO20
GPIO21: microcontroller.Pin  # GPIO21
GPIO26: microcontroller.Pin  # GPIO26
GPIO48: microcontroller.Pin  # GPIO48
GPIO47: microcontroller.Pin  # GPIO47
GPIO33: microcontroller.Pin  # GPIO33
GPIO34: microcontroller.Pin  # GPIO34
GPIO35: microcontroller.Pin  # GPIO35
GPIO36: microcontroller.Pin  # GPIO36
GPIO0: microcontroller.Pin  # GPIO0
GPIO43: microcontroller.Pin  # GPIO43
GPIO44: microcontroller.Pin  # GPIO44
BAT_ADC: microcontroller.Pin  # GPIO1
USER_BUTTON: microcontroller.Pin  # GPIO0
TOUCH1: microcontroller.Pin  # GPIO1
TOUCH2: microcontroller.Pin  # GPIO2
TOUCH3: microcontroller.Pin  # GPIO3
TOUCH4: microcontroller.Pin  # GPIO4
TOUCH5: microcontroller.Pin  # GPIO5
TOUCH6: microcontroller.Pin  # GPIO6
TOUCH7: microcontroller.Pin  # GPIO7
ADC2_CH9A: microcontroller.Pin  # GPIO19
ADC1_CH9B: microcontroller.Pin  # GPIO20
LED: microcontroller.Pin  # GPIO35
DEBUG_TX: microcontroller.Pin  # GPIO43
DEBUG_RX: microcontroller.Pin  # GPIO44
LORA_NSS: microcontroller.Pin  # GPIO8
LORA_SCK: microcontroller.Pin  # GPIO9
LORA_MOSI: microcontroller.Pin  # GPIO10
LORA_MISO: microcontroller.Pin  # GPIO11
LORA_RST: microcontroller.Pin  # GPIO12
LORA_BUSY: microcontroller.Pin  # GPIO13
OLED_RST: microcontroller.Pin  # GPIO21
OLED_SDA: microcontroller.Pin  # GPIO17
OLED_SCL: microcontroller.Pin  # GPIO18


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

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
