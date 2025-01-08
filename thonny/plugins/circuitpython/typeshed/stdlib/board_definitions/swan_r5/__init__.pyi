# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Swan R5
 - port: stm
 - board_id: swan_r5
 - NVM size: Unknown
 - Included modules: _asyncio, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # PD09
D1: microcontroller.Pin  # PD08
D2: microcontroller.Pin  # PF15
D3: microcontroller.Pin  # PE13
D4: microcontroller.Pin  # PE03
SCK: microcontroller.Pin  # PD01
MOSI: microcontroller.Pin  # PB15
MISO: microcontroller.Pin  # PB14
CS: microcontroller.Pin  # PD00
RTS: microcontroller.Pin  # PG12
CTS: microcontroller.Pin  # PB04
RX0: microcontroller.Pin  # PG08
TX0: microcontroller.Pin  # PG07
A0: microcontroller.Pin  # PA03
A1: microcontroller.Pin  # PA01
A2: microcontroller.Pin  # PC03
A3: microcontroller.Pin  # PC01
A4: microcontroller.Pin  # PC04
A5: microcontroller.Pin  # PC05
A6: microcontroller.Pin  # PB01
A7: microcontroller.Pin  # PC02
D14: microcontroller.Pin  # PB09
D15: microcontroller.Pin  # PE01
RX: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA09
SCL3: microcontroller.Pin  # PC00
SDA3: microcontroller.Pin  # PC09
RX2: microcontroller.Pin  # PD06
RTS2: microcontroller.Pin  # PD04
CTS2: microcontroller.Pin  # PD03
TX3: microcontroller.Pin  # PB10
RX3: microcontroller.Pin  # PB11
RTS3: microcontroller.Pin  # PD02
CTS3: microcontroller.Pin  # PB13
D6: microcontroller.Pin  # PE09
D5: microcontroller.Pin  # PE11
SCL2: microcontroller.Pin  # PF01
SDA2: microcontroller.Pin  # PF00
QEN: microcontroller.Pin  # PD05
QCS: microcontroller.Pin  # PC11
QCLK: microcontroller.Pin  # PE10
EN: microcontroller.Pin  # PE04
TX2: microcontroller.Pin  # PA02
D13: microcontroller.Pin  # PA05
D12: microcontroller.Pin  # PA06
D11: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA04
D9: microcontroller.Pin  # PD15
D8: microcontroller.Pin  # PF12
D7: microcontroller.Pin  # PF13
SCL: microcontroller.Pin  # PB06
SDA: microcontroller.Pin  # PB07
QIO3: microcontroller.Pin  # PE15
QIO2: microcontroller.Pin  # PE14
QIO1: microcontroller.Pin  # PB00
QIO0: microcontroller.Pin  # PE12
A0: microcontroller.Pin  # PA03
A1: microcontroller.Pin  # PA01
A2: microcontroller.Pin  # PC03
A3: microcontroller.Pin  # PC01
A4: microcontroller.Pin  # PC04
A5: microcontroller.Pin  # PC05
VOLTAGE_MONITOR: microcontroller.Pin  # PA00
BUTTON_USR: microcontroller.Pin  # PC13
SWITCH: microcontroller.Pin  # PE04
BUTTON: microcontroller.Pin  # PB02
D5: microcontroller.Pin  # PE11
D6: microcontroller.Pin  # PE09
D9: microcontroller.Pin  # PD15
D10: microcontroller.Pin  # PA04
D11: microcontroller.Pin  # PA07
D12: microcontroller.Pin  # PA06
LED: microcontroller.Pin  # PE02
D13: microcontroller.Pin  # PA05
SDA: microcontroller.Pin  # PB07
SCL: microcontroller.Pin  # PB06
DAC1: microcontroller.Pin  # PA04
DAC2: microcontroller.Pin  # PA05
SS: microcontroller.Pin  # PD00
SCK: microcontroller.Pin  # PD01
MISO: microcontroller.Pin  # PB14
MOSI: microcontroller.Pin  # PB15
TX: microcontroller.Pin  # PA09
RX: microcontroller.Pin  # PA10
MICROPHONE_CLOCK: microcontroller.Pin  # PA03
MICROPHONE_DATA: microcontroller.Pin  # PC03


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#     { MP_ROM_QSTR(MP_QSTR_ext), MP_ROM_PTR(&carrier_type) },
