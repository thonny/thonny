# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO T-Watch-S3
 - port: espressif
 - board_id: lilygo_twatch_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_drv2605, adafruit_focaltouch, adafruit_irremote, adafruit_pcf8563, adafruit_register, axp2101, bma423
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TFT_MOSI: microcontroller.Pin  # GPIO13
TFT_SCLK: microcontroller.Pin  # GPIO18
TFT_CS: microcontroller.Pin  # GPIO12
TFT_DC: microcontroller.Pin  # GPIO38
TFT_BL: microcontroller.Pin  # GPIO45
TOUCH_INT: microcontroller.Pin  # GPIO16
TOUCH_SCL: microcontroller.Pin  # GPIO40
TOUCH_SDA: microcontroller.Pin  # GPIO39
RTC_INT: microcontroller.Pin  # GPIO17
IR_LED: microcontroller.Pin  # GPIO2
PMU_INT: microcontroller.Pin  # GPIO21
RADIO_SCK: microcontroller.Pin  # GPIO3
RADIO_MISO: microcontroller.Pin  # GPIO4
RADIO_MOSI: microcontroller.Pin  # GPIO1
RADIO_SS: microcontroller.Pin  # GPIO5
RADIO_DIO1: microcontroller.Pin  # GPIO9
RADIO_RST: microcontroller.Pin  # GPIO8
RADIO_BUSY: microcontroller.Pin  # GPIO7
MIC_DATA: microcontroller.Pin  # GPIO47
MIC_SCLK: microcontroller.Pin  # GPIO44
I2S_BCK: microcontroller.Pin  # GPIO48
I2S_WS: microcontroller.Pin  # GPIO15
I2S_DOUT: microcontroller.Pin  # GPIO46
AXIS_INT: microcontroller.Pin  # GPIO14
I2C_SCL: microcontroller.Pin  # GPIO11
I2C_SDA: microcontroller.Pin  # GPIO10
BOOT: microcontroller.Pin  # GPIO0


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
