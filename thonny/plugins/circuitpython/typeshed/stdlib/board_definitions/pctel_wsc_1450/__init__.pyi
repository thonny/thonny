# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for WSC-1450
 - port: nordic
 - board_id: pctel_wsc_1450
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
32KHZ_XTAL1: microcontroller.Pin  # P0_00
32KHZ_XTAL2: microcontroller.Pin  # P0_01
BATTERY: microcontroller.Pin  # P0_02
BOARD_ID: microcontroller.Pin  # P0_03
INT_LIGHT_TOF: microcontroller.Pin  # P0_04
LED_RED: microcontroller.Pin  # P0_05
I2S_SCK: microcontroller.Pin  # P0_06
LORA_SCLK: microcontroller.Pin  # P0_07
I2S_WS: microcontroller.Pin  # P0_08
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
LORA_MOSI: microcontroller.Pin  # P0_11
LORA_MISO: microcontroller.Pin  # P0_12
DEBUG_TX: microcontroller.Pin  # P0_13
CELL_RTS: microcontroller.Pin  # P0_14
CELL_DCD: microcontroller.Pin  # P0_15
DEBUG_RX: microcontroller.Pin  # P0_16
QSPI_CSN: microcontroller.Pin  # P0_17
BT840_RESETN: microcontroller.Pin  # P0_18
QSPI_CLK: microcontroller.Pin  # P0_19
QSPI_IO0: microcontroller.Pin  # P0_20
QSPI_IO1: microcontroller.Pin  # P0_21
QSPI_IO2: microcontroller.Pin  # P0_22
QSPI_IO3: microcontroller.Pin  # P0_23
CELL_HW_SHUTDOWN: microcontroller.Pin  # P0_24
I2S_SD: microcontroller.Pin  # P0_25
SDA: microcontroller.Pin  # P0_26
SCL: microcontroller.Pin  # P0_27
CELL_POWER_ENABLE: microcontroller.Pin  # P0_28
PUSH_BUTTON: microcontroller.Pin  # P0_29
CELL_ON_OFF: microcontroller.Pin  # P0_30
SENSOR_POWER_ENABLE: microcontroller.Pin  # P0_31
BT840_SWO: microcontroller.Pin  # P1_00
CELL_RX: microcontroller.Pin  # P1_01
CELL_TX: microcontroller.Pin  # P1_02
CELL_DSR: microcontroller.Pin  # P1_03
CELL_DTR: microcontroller.Pin  # P1_04
INT_ACCEL: microcontroller.Pin  # P1_05
BOARD_ID_DISABLE: microcontroller.Pin  # P1_06
LORA_DIO0: microcontroller.Pin  # P1_07
CELL_CTS: microcontroller.Pin  # P1_08
LORA_SSN: microcontroller.Pin  # P1_09
LORA_RESETN: microcontroller.Pin  # P1_10
BATTERY_MONITOR_ENABLE: microcontroller.Pin  # P1_11
LORA_DIO1: microcontroller.Pin  # P1_12
LORA_DIO2: microcontroller.Pin  # P1_13
LORA_DIO3: microcontroller.Pin  # P1_14
CELL_PWRMON: microcontroller.Pin  # P1_15
LORA_DIO4: microcontroller.Pin  # P1_15


# Members:

# Unmapped:
#   none
