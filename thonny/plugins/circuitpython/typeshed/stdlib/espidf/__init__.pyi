from __future__ import annotations

import builtins

"""Direct access to a few ESP-IDF details. This module *should not* include any functionality
   that could be implemented by other frameworks. It should only include ESP-IDF specific
   things."""

def heap_caps_get_total_size() -> int:
    """Return the total size of the ESP-IDF, which includes the CircuitPython heap."""
    ...

def heap_caps_get_free_size() -> int:
    """Return total free memory in the ESP-IDF heap."""
    ...

def heap_caps_get_largest_free_block() -> int:
    """Return the size of largest free memory block in the ESP-IDF heap."""
    ...

def erase_nvs() -> None:
    """Erase all data in the non-volatile storage (nvs), including data stored by with `microcontroller.nvm`

    This is necessary when upgrading from CircuitPython 6.3.0 or earlier to CircuitPython 7.0.0, because the
    layout of data in nvs has changed. The old data will be lost when you perform this operation.
    """

class IDFError(builtins.OSError):
    """Raised when an ``ESP-IDF`` function returns an error code.
    `esp_err_t <https://docs.espressif.com/projects/esp-idf/en/release-v4.4/esp32/api-reference/error-codes.html>`_
    """

    ...

class MemoryError(builtins.MemoryError):
    """Raised when an ``ESP-IDF`` memory allocation fails."""

    ...

def get_total_psram() -> int:
    """Returns the number of bytes of psram detected, or 0 if psram is not present or not configured"""
