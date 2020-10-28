"""Supervisor settings"""

runtime: Runtime = ...
"""Runtime information, such as ``runtime.serial_connected``
(USB serial connection status).
This object is the sole instance of `supervisor.Runtime`."""

def enable_autoreload(self) -> None:
    """Enable autoreload based on USB file write activity."""
    ...

def disable_autoreload(self) -> None:
    """Disable autoreload based on USB file write activity until
    `enable_autoreload` is called."""
    ...

def set_rgb_status_brightness(self, brightness: int) -> None:
    """Set brightness of status neopixel from 0-255
    `set_rgb_status_brightness` is called."""
    ...

def reload(self) -> None:
    """Reload the main Python code and run it (equivalent to hitting Ctrl-D at the REPL)."""
    ...

def set_next_stack_limit(self, size: int) -> None:
    """Set the size of the stack for the next vm run. If its too large, the default will be used."""
    ...

class Runtime:
    """Current status of runtime objects.

    Usage::

       import supervisor
       if supervisor.runtime.serial_connected:
           print("Hello World!")"""

    def __init__(self, ):
        """You cannot create an instance of `supervisor.Runtime`.
        Use `supervisor.runtime` to access the sole instance available."""
        ...

    serial_connected: bool = ...
    """Returns the USB serial communication status (read-only).

    .. note::

        SAMD: Will return ``True`` if the USB serial connection
        has been established at any point.  Will not reset if
        USB is disconnected but power remains (e.g. battery connected)"""

    serial_bytes_available: int = ...
    """Returns the whether any bytes are available to read
    on the USB serial input.  Allows for polling to see whether
    to call the built-in input() or wait. (read-only)"""

