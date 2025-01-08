# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for STM32F412G_DISCO
 - port: stm
 - board_id: stm32f412zg_discovery
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
PE02: microcontroller.Pin  # PE02
PE03: microcontroller.Pin  # PE03
PE04: microcontroller.Pin  # PE04
PE05: microcontroller.Pin  # PE05
PE06: microcontroller.Pin  # PE06
PC13: microcontroller.Pin  # PC13
PF02: microcontroller.Pin  # PF02
PF03: microcontroller.Pin  # PF03
PF10: microcontroller.Pin  # PF10
PC00: microcontroller.Pin  # PC00
PC01: microcontroller.Pin  # PC01
PC02: microcontroller.Pin  # PC02
PC03: microcontroller.Pin  # PC03
PA01: microcontroller.Pin  # PA01
PA02: microcontroller.Pin  # PA02
PA03: microcontroller.Pin  # PA03
PA04: microcontroller.Pin  # PA04
PA05: microcontroller.Pin  # PA05
PA06: microcontroller.Pin  # PA06
PA07: microcontroller.Pin  # PA07
PC04: microcontroller.Pin  # PC04
PC05: microcontroller.Pin  # PC05
PB00: microcontroller.Pin  # PB00
PB01: microcontroller.Pin  # PB01
PF11: microcontroller.Pin  # PF11
PF13: microcontroller.Pin  # PF13
PB10: microcontroller.Pin  # PB10
PB11: microcontroller.Pin  # PB11
PB12: microcontroller.Pin  # PB12
PB13: microcontroller.Pin  # PB13
PB14: microcontroller.Pin  # PB14
PB15: microcontroller.Pin  # PB15
PD12: microcontroller.Pin  # PD12
PD13: microcontroller.Pin  # PD13
PG02: microcontroller.Pin  # PG02
PC06: microcontroller.Pin  # PC06
PC07: microcontroller.Pin  # PC07
PC09: microcontroller.Pin  # PC09
PA08: microcontroller.Pin  # PA08
PA10: microcontroller.Pin  # PA10
PA13: microcontroller.Pin  # PA13
PA14: microcontroller.Pin  # PA14
PA15: microcontroller.Pin  # PA15
PD06: microcontroller.Pin  # PD06
PG09: microcontroller.Pin  # PG09
PG10: microcontroller.Pin  # PG10
PG11: microcontroller.Pin  # PG11
PG12: microcontroller.Pin  # PG12
PG13: microcontroller.Pin  # PG13
PG14: microcontroller.Pin  # PG14
PB03: microcontroller.Pin  # PB03
PB04: microcontroller.Pin  # PB04
PB05: microcontroller.Pin  # PB05
PB06: microcontroller.Pin  # PB06
PB07: microcontroller.Pin  # PB07
PB08: microcontroller.Pin  # PB08
PB09: microcontroller.Pin  # PB09
PE00: microcontroller.Pin  # PE00
PE01: microcontroller.Pin  # PE01
D15: microcontroller.Pin  # PB10
D14: microcontroller.Pin  # PB09
D13: microcontroller.Pin  # PA05
D12: microcontroller.Pin  # PA06
D11: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA15
D9: microcontroller.Pin  # PB08
D8: microcontroller.Pin  # PG10
D7: microcontroller.Pin  # PG11
D6: microcontroller.Pin  # PF03
D5: microcontroller.Pin  # PF10
D4: microcontroller.Pin  # PG12
D3: microcontroller.Pin  # PF04
D2: microcontroller.Pin  # PG13
D1: microcontroller.Pin  # PG14
D0: microcontroller.Pin  # PG09
A0: microcontroller.Pin  # PA01
A1: microcontroller.Pin  # PC01
A2: microcontroller.Pin  # PC03
A3: microcontroller.Pin  # PC04
A4: microcontroller.Pin  # PC05
A5: microcontroller.Pin  # PB00
SCL: microcontroller.Pin  # PB10
SDA: microcontroller.Pin  # PB09
LED1: microcontroller.Pin  # PE00
LED2: microcontroller.Pin  # PE01
LED3: microcontroller.Pin  # PE02
LED4: microcontroller.Pin  # PE03


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
