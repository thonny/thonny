"""USB Host

The `usb_host` module allows you to manage USB host ports. To communicate
with devices use the `usb` module that is a subset of PyUSB's API.
"""

from __future__ import annotations

import microcontroller

class Port:
    """USB host port. Also known as a root hub port."""

    def __init__(self, dp: microcontroller.Pin, dm: microcontroller.Pin) -> None:
        """Create a USB host port on the given pins. Access attached devices
        through the `usb` module. Keep this object referenced while
        interacting with devices, otherwise they will be disconnected.

        :param ~microcontroller.Pin dp: The data plus pin
        :param ~microcontroller.Pin dm: The data minus pin
        """
        ...
    def deinit(self) -> None:
        """Turn off the USB host port and release the pins for other use."""
        ...
    def __enter__(self) -> Port:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
