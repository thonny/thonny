# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Freenove ESP32-WROVER-DEV-CAM
 - port: espressif
 - board_id: esp32-wrover-dev-cam
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # GPIO2
LED_INVERTED: microcontroller.Pin  # GPIO2
BUTTON: microcontroller.Pin  # GPIO0
CAMERA_DATA2: microcontroller.Pin  # GPIO4
CAMERA_DATA3: microcontroller.Pin  # GPIO5
CAMERA_DATA4: microcontroller.Pin  # GPIO18
CAMERA_DATA5: microcontroller.Pin  # GPIO19
CAMERA_DATA6: microcontroller.Pin  # GPIO36
CAMERA_DATA7: microcontroller.Pin  # GPIO39
CAMERA_DATA8: microcontroller.Pin  # GPIO34
CAMERA_DATA9: microcontroller.Pin  # GPIO35
CAMERA_HREF: microcontroller.Pin  # GPIO23
CAMERA_PCLK: microcontroller.Pin  # GPIO22
CAMERA_PWDN: microcontroller.Pin  # GPIO32
CAMERA_VSYNC: microcontroller.Pin  # GPIO25
CAMERA_XCLK: microcontroller.Pin  # GPIO21
CAMERA_SIOD: microcontroller.Pin  # GPIO26
CAMERA_SIOC: microcontroller.Pin  # GPIO27
FLASH_D2: microcontroller.Pin  # GPIO9
FLASH_D3: microcontroller.Pin  # GPIO10
FLASH_CMD: microcontroller.Pin  # GPIO11
FLASH_D1: microcontroller.Pin  # GPIO8
FLASH_D0: microcontroller.Pin  # GPIO7
FLASH_CLK: microcontroller.Pin  # GPIO6
SENSOR_VP: microcontroller.Pin  # GPIO36
CAM_Y6: microcontroller.Pin  # GPIO36
ADC1_CH0: microcontroller.Pin  # GPIO36
SENSOR_VN: microcontroller.Pin  # GPIO39
CAM_Y7: microcontroller.Pin  # GPIO39
ADC1_CH3: microcontroller.Pin  # GPIO39
CAM_Y8: microcontroller.Pin  # GPIO34
ADC1_CH6: microcontroller.Pin  # GPIO34
CAM_Y9: microcontroller.Pin  # GPIO35
ADC1_CH7: microcontroller.Pin  # GPIO35
TOUCH9: microcontroller.Pin  # GPIO32
ADC1_CH4: microcontroller.Pin  # GPIO32
TOUCH8: microcontroller.Pin  # GPIO33
ADC1_CH5: microcontroller.Pin  # GPIO33
I2S_LCK: microcontroller.Pin  # GPIO25
DAC1: microcontroller.Pin  # GPIO25
CAM_VSYNC: microcontroller.Pin  # GPIO25
ADC2_CH8: microcontroller.Pin  # GPIO25
I2S_BCK: microcontroller.Pin  # GPIO26
DAC2: microcontroller.Pin  # GPIO26
CAM_SIOD: microcontroller.Pin  # GPIO26
SDA2: microcontroller.Pin  # GPIO26
ADC2_CH9: microcontroller.Pin  # GPIO26
TOUCH7: microcontroller.Pin  # GPIO27
CAM_SIOC: microcontroller.Pin  # GPIO27
SCL2: microcontroller.Pin  # GPIO27
ADC2_CH7: microcontroller.Pin  # GPIO27
TOUCH6: microcontroller.Pin  # GPIO14
HSPI_CLK: microcontroller.Pin  # GPIO14
ADC2_CH6: microcontroller.Pin  # GPIO14
MTDI: microcontroller.Pin  # GPIO12
TOUCH5: microcontroller.Pin  # GPIO12
HSPI_MISO: microcontroller.Pin  # GPIO12
ADC2_CH5: microcontroller.Pin  # GPIO12
TOUCH4: microcontroller.Pin  # GPIO13
HSPI_MOSI: microcontroller.Pin  # GPIO13
ADC2_CH4: microcontroller.Pin  # GPIO13
CAM_HREF: microcontroller.Pin  # GPIO23
VSPI_MOSI: microcontroller.Pin  # GPIO23
I2S: microcontroller.Pin  # GPIO22
DIN: microcontroller.Pin  # GPIO22
CAM_PCLK: microcontroller.Pin  # GPIO22
I2C_SCL: microcontroller.Pin  # GPIO22
LED_TX: microcontroller.Pin  # GPIO1
U0TXD: microcontroller.Pin  # GPIO1
LED_RX: microcontroller.Pin  # GPIO3
U0RXD: microcontroller.Pin  # GPIO3
CAM_XCLK: microcontroller.Pin  # GPIO21
I2C_SDA: microcontroller.Pin  # GPIO21
CAM_Y5: microcontroller.Pin  # GPIO19
VSPI_MISO: microcontroller.Pin  # GPIO19
CAM_Y4: microcontroller.Pin  # GPIO18
VSPI_CLK: microcontroller.Pin  # GPIO18
CAM_Y3: microcontroller.Pin  # GPIO5
VSPI_CS: microcontroller.Pin  # GPIO5
SDIO_SLAVE: microcontroller.Pin  # GPIO5
TOUCH0: microcontroller.Pin  # GPIO4
CAM_Y2: microcontroller.Pin  # GPIO4
ADC2_CH0: microcontroller.Pin  # GPIO4
TOUCH1: microcontroller.Pin  # GPIO0
ADC2_CH1: microcontroller.Pin  # GPIO0
TOUCH2: microcontroller.Pin  # GPIO2
ADC2_CH2: microcontroller.Pin  # GPIO2
LED_IO2: microcontroller.Pin  # GPIO2
TOUCH3: microcontroller.Pin  # GPIO15
MTDO: microcontroller.Pin  # GPIO15
ADC2_CH3: microcontroller.Pin  # GPIO15
HSPI_CS: microcontroller.Pin  # GPIO15
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
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO21: microcontroller.Pin  # GPIO21
IO22: microcontroller.Pin  # GPIO22
IO23: microcontroller.Pin  # GPIO23
IO25: microcontroller.Pin  # GPIO25
IO26: microcontroller.Pin  # GPIO26
IO27: microcontroller.Pin  # GPIO27
IO32: microcontroller.Pin  # GPIO32
IO33: microcontroller.Pin  # GPIO33
IO34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO39: microcontroller.Pin  # GPIO39
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO13


# Members:
CAMERA_DATA: Tuple[Any]

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
