"""
functions related to the ESP8266 and ESP32.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/esp.rst.
=========================================================

.. module:: esp
    :synopsis: functions related to the ESP8266 and ESP32

The ``esp`` module contains specific functions related to both the ESP8266 and 
ESP32 modules.  Some functions are only available on one or the other of these
ports.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final, overload

from uio import AnyWritableBuf, AnyReadableBuf

SLEEP_NONE: Final[int] = ...
"""All functions enabled."""

SLEEP_MODEM: Final[int] = ...
"""Modem sleep, shuts down the WiFi Modem circuit."""

SLEEP_LIGHT: Final[int] = ...
"""Light sleep, shuts down the WiFi Modem circuit."""

# noinspection PyShadowingNames
@overload
def sleep_type(sleep_type: int, /) -> None:
    """
    **Note**: ESP8266 only
    
    Get or set the sleep type.
    
    If the *sleep_type* parameter is provided, sets the sleep type to its
    value. If the function is called without parameters, returns the current
    sleep type.
    
    The possible sleep types are defined as constants:
    
        * ``SLEEP_NONE`` -- all functions enabled,
        * ``SLEEP_MODEM`` -- modem sleep, shuts down the WiFi Modem circuit.
        * ``SLEEP_LIGHT`` -- light sleep, shuts down the WiFi Modem circuit
          and suspends the processor periodically.
    
    The system enters the set sleep mode automatically when possible.
   """

# noinspection PyShadowingNames
@overload
def sleep_type() -> int:
    """
    **Note**: ESP8266 only
    
    Get or set the sleep type.
    
    If the *sleep_type* parameter is provided, sets the sleep type to its
    value. If the function is called without parameters, returns the current
    sleep type.
    
    The possible sleep types are defined as constants:
    
        * ``SLEEP_NONE`` -- all functions enabled,
        * ``SLEEP_MODEM`` -- modem sleep, shuts down the WiFi Modem circuit.
        * ``SLEEP_LIGHT`` -- light sleep, shuts down the WiFi Modem circuit
          and suspends the processor periodically.
    
    The system enters the set sleep mode automatically when possible.
   """

def deepsleep(time_us: int = 0, /) -> None:
    """
    **Note**: ESP8266 only - use `machine.deepsleep()` on ESP32
    
    Enter deep sleep.
    
    The whole module powers down, except for the RTC clock circuit, which can
    be used to restart the module after the specified time if the pin 16 is
    connected to the reset pin. Otherwise the module will sleep until manually
    reset.
   """

def flash_id() -> int:
    """
    **Note**: ESP8266 only
    
    Read the device ID of the flash memory.
   """

def flash_size() -> int:
    """
    Read the total size of the flash memory.
   """

def flash_user_start() -> int:
    """
    Read the memory offset at which the user flash space begins.
   """

@overload
def flash_read(byte_offset: int, length_or_buffer: int, /) -> bytes:
    """
   Reads bytes from the flash memory starting at the given byte offset.
   If length is specified: reads the given length of bytes and returns them as ``bytes``.
   If a buffer is given: reads the buf length of bytes and writes them into the buffer.
   Note: esp32 doesn't support passing a length, just a buffer.
   """

@overload
def flash_read(byte_offset: int, length_or_buffer: AnyWritableBuf, /) -> None:
    """
   Reads bytes from the flash memory starting at the given byte offset.
   If length is specified: reads the given length of bytes and returns them as ``bytes``.
   If a buffer is given: reads the buf length of bytes and writes them into the buffer.
   Note: esp32 doesn't support passing a length, just a buffer.
   """

def flash_write(byte_offset: int, bytes: AnyReadableBuf, /) -> None:
    """
   Writes given bytes buffer to the flash memory starting at the given byte offset.
   """

def flash_erase(sector_no: int, /) -> None:
    """
   Erases the given *sector* of flash memory.
   """

@overload
def set_native_code_location(start: None, length: None, /) -> None:
    """
    **Note**: ESP8266 only
    
    Set the location that native code will be placed for execution after it is
    compiled.  Native code is emitted when the ``@micropython.native``,
    ``@micropython.viper`` and ``@micropython.asm_xtensa`` decorators are applied
    to a function.  The ESP8266 must execute code from either iRAM or the lower
    1MByte of flash (which is memory mapped), and this function controls the
    location.
    
    If *start* and *length* are both ``None`` then the native code location is
    set to the unused portion of memory at the end of the iRAM1 region.  The
    size of this unused portion depends on the firmware and is typically quite
    small (around 500 bytes), and is enough to store a few very small
    functions.  The advantage of using this iRAM1 region is that it does not
    get worn out by writing to it.
    
    If neither *start* nor *length* are ``None`` then they should be integers.
    *start* should specify the byte offset from the beginning of the flash at
    which native code should be stored.  *length* specifies how many bytes of
    flash from *start* can be used to store native code.  *start* and *length*
    should be multiples of the sector size (being 4096 bytes).  The flash will
    be automatically erased before writing to it so be sure to use a region of
    flash that is not otherwise used, for example by the firmware or the
    filesystem.
    
    When using the flash to store native code *start+length* must be less
    than or equal to 1MByte.  Note that the flash can be worn out if repeated
    erasures (and writes) are made so use this feature sparingly.
    In particular, native code needs to be recompiled and rewritten to flash
    on each boot (including wake from deepsleep).
    
    In both cases above, using iRAM1 or flash, if there is no more room left
    in the specified region then the use of a native decorator on a function
    will lead to `MemoryError` exception being raised during compilation of
    that function.
   """

@overload
def set_native_code_location(start: int, length: int, /) -> None:
    """
    **Note**: ESP8266 only
    
    Set the location that native code will be placed for execution after it is
    compiled.  Native code is emitted when the ``@micropython.native``,
    ``@micropython.viper`` and ``@micropython.asm_xtensa`` decorators are applied
    to a function.  The ESP8266 must execute code from either iRAM or the lower
    1MByte of flash (which is memory mapped), and this function controls the
    location.
    
    If *start* and *length* are both ``None`` then the native code location is
    set to the unused portion of memory at the end of the iRAM1 region.  The
    size of this unused portion depends on the firmware and is typically quite
    small (around 500 bytes), and is enough to store a few very small
    functions.  The advantage of using this iRAM1 region is that it does not
    get worn out by writing to it.
    
    If neither *start* nor *length* are ``None`` then they should be integers.
    *start* should specify the byte offset from the beginning of the flash at
    which native code should be stored.  *length* specifies how many bytes of
    flash from *start* can be used to store native code.  *start* and *length*
    should be multiples of the sector size (being 4096 bytes).  The flash will
    be automatically erased before writing to it so be sure to use a region of
    flash that is not otherwise used, for example by the firmware or the
    filesystem.
    
    When using the flash to store native code *start+length* must be less
    than or equal to 1MByte.  Note that the flash can be worn out if repeated
    erasures (and writes) are made so use this feature sparingly.
    In particular, native code needs to be recompiled and rewritten to flash
    on each boot (including wake from deepsleep).
    
    In both cases above, using iRAM1 or flash, if there is no more room left
    in the specified region then the use of a native decorator on a function
    will lead to `MemoryError` exception being raised during compilation of
    that function.
   """
