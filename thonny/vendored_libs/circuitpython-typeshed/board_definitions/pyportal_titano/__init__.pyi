# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit PyPortal Titano
 - port: atmel-samd
 - board_id: pyportal_titano
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, spitarget, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_display_text, adafruit_esp32spi, adafruit_fakerequests, adafruit_portalbase, adafruit_requests, neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
SPEAKER: microcontroller.Pin  # PA02
AUDIO_OUT: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA02
SPEAKER_ENABLE: microcontroller.Pin  # PA27
LIGHT: microcontroller.Pin  # PA07
A2: microcontroller.Pin  # PA07
D3: microcontroller.Pin  # PA04
A1: microcontroller.Pin  # PA04
D4: microcontroller.Pin  # PA05
A4: microcontroller.Pin  # PA05
LED: microcontroller.Pin  # PB23
D13: microcontroller.Pin  # PB23
L: microcontroller.Pin  # PB23
NEOPIXEL: microcontroller.Pin  # PB22
TFT_RESET: microcontroller.Pin  # PA00
TFT_RD: microcontroller.Pin  # PB04
TFT_RS: microcontroller.Pin  # PB05
TFT_CS: microcontroller.Pin  # PB06
TFT_TE: microcontroller.Pin  # PB07
TFT_WR: microcontroller.Pin  # PB09
TFT_DC: microcontroller.Pin  # PB09
TFT_BACKLIGHT: microcontroller.Pin  # PB31
LCD_DATA0: microcontroller.Pin  # PA16
LCD_DATA1: microcontroller.Pin  # PA17
LCD_DATA2: microcontroller.Pin  # PA18
LCD_DATA3: microcontroller.Pin  # PA19
LCD_DATA4: microcontroller.Pin  # PA20
LCD_DATA5: microcontroller.Pin  # PA21
LCD_DATA6: microcontroller.Pin  # PA22
LCD_DATA7: microcontroller.Pin  # PA23
TOUCH_YD: microcontroller.Pin  # PB00
TOUCH_XL: microcontroller.Pin  # PB01
TOUCH_YU: microcontroller.Pin  # PA06
TOUCH_XR: microcontroller.Pin  # PB08
ESP_CS: microcontroller.Pin  # PB14
ESP_GPIO0: microcontroller.Pin  # PB15
ESP_BUSY: microcontroller.Pin  # PB16
ESP_RESET: microcontroller.Pin  # PB17
ESP_RTS: microcontroller.Pin  # PA15
ESP_TX: microcontroller.Pin  # PB12
ESP_RX: microcontroller.Pin  # PB13
MOSI: microcontroller.Pin  # PA12
SCK: microcontroller.Pin  # PA13
MISO: microcontroller.Pin  # PA14
SDA: microcontroller.Pin  # PB02
SCL: microcontroller.Pin  # PB03
SD_CS: microcontroller.Pin  # PB30
SD_CARD_DETECT: microcontroller.Pin  # PA01


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
