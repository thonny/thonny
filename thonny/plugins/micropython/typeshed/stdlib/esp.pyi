"""
Functions related to the ESP8266 and ESP32.

MicroPython module: https://docs.micropython.org/en/v1.23.0/library/esp.html

The ``esp`` module contains specific functions related to both the ESP8266 and
ESP32 modules.  Some functions are only available on one or the other of these
ports.

---
Module: 'esp' on micropython-v1.23.0-esp32-ESP32_GENERIC
"""

# MCU: {'version': '1.23.0', 'mpy': 'v6.3', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'family': 'micropython', 'build': '', 'arch': 'xtensawin', 'ver': '1.23.0', 'cpu': 'ESP32'}
# Stubber: v1.23.0
from __future__ import annotations
from _typeshed import Incomplete
from typing import Any, Optional

LOG_NONE: int = 0
LOG_WARNING: int = 2
LOG_VERBOSE: int = 5
LOG_DEBUG: int = 4
LOG_INFO: int = 3
LOG_ERROR: int = 1

def osdebug(uart_no, level: Optional[Any] = None) -> Incomplete:
    """
    :no-index:

    ``Note:`` This is the ESP32 form of this function.

    Change the level of OS serial debug log messages. On boot, OS
    serial debug log messages are limited to Error output only.

    The behaviour of this function depends on the arguments passed to it. The
    following combinations are supported:

    ``osdebug(None)`` restores the default OS debug log message level
    (``LOG_ERROR``).

    ``osdebug(0)`` enables all available OS debug log messages (in the
    default build configuration this is ``LOG_INFO``).

    ``osdebug(0, level)`` sets the OS debug log message level to the
     specified value. The log levels are defined as constants:

        * ``LOG_NONE`` -- No log output
        * ``LOG_ERROR`` -- Critical errors, software module can not recover on its own
        * ``LOG_WARN`` -- Error conditions from which recovery measures have been taken
        * ``LOG_INFO`` -- Information messages which describe normal flow of events
        * ``LOG_DEBUG`` -- Extra information which is not necessary for normal use (values, pointers, sizes, etc)
        * ``LOG_VERBOSE`` -- Bigger chunks of debugging information, or frequent messages
          which can potentially flood the output

    ``Note:`` ``LOG_DEBUG`` and ``LOG_VERBOSE`` are not compiled into the
              MicroPython binary by default, to save size. A custom build with a
              modified "``sdkconfig``" source file is needed to see any output
              at these log levels.

    ``Note:`` Log output on ESP32 is automatically suspended in "Raw REPL" mode,
              to prevent communications issues. This means OS level logging is never
              seen when using ``mpremote run`` and similar tools.
    """
    ...

def flash_write(byte_offset, bytes) -> Incomplete: ...
def gpio_matrix_in(*args, **kwargs) -> Incomplete: ...
def gpio_matrix_out(*args, **kwargs) -> Incomplete: ...
def flash_user_start() -> Incomplete:
    """
    Read the memory offset at which the user flash space begins.
    """
    ...

def flash_erase(sector_no) -> Incomplete: ...
def flash_read(byte_offset, length_or_buffer) -> Incomplete: ...
def flash_size() -> Incomplete:
    """
    Read the total size of the flash memory.
    """
    ...
