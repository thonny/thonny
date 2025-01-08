"""USB Host

The `usb_host` module allows you to manage USB host ports. To communicate
with devices use the `usb` module that is a subset of PyUSB's API.
"""

from __future__ import annotations

import microcontroller
from circuitpython_typing import ReadableBuffer

def set_user_keymap(keymap: ReadableBuffer, /) -> None:
    """Set the keymap used by a USB HID keyboard in kernel mode

    The keymap consists of 256 or 384 1-byte entries that map from USB keycodes
    to ASCII codes. The first 128 entries are for unmodified keys,
    the next 128 entries are for shifted keys,and the next optional 128 entries are
    for altgr-modified keys.

    The values must all be ASCII (32 through 126 inclusive); other values are not valid.

    The values at index 0, 128, and 256 (if the keymap has 384 entries) must be
    0; other values are reserved for future expansion to indicate alternate
    keymap formats.

    At other indices, the value 0 is used to indicate that the normal
    definition is still used. For instance, the entry for HID_KEY_ARROW_UP
    (0x52) is usually 0 so that the default behavior of sending an escape code
    is preserved.

    This function is a CircuitPython extension not present in PyUSB
    """

class Port:
    """USB host port. Also known as a root hub port."""

    def __init__(self, dp: microcontroller.Pin, dm: microcontroller.Pin) -> None:
        """Create a USB host port on the given pins. Access attached devices
        through the `usb` module.

        The resulting object lives longer than the CircuitPython VM so that
        USB devices such as keyboards can continue to be used. Subsequent
        calls to this constructor will return the same object and *not*
        reinitialize the USB host port. It will raise an exception when
        given different arguments from the first successful call.

        :param ~microcontroller.Pin dp: The data plus pin
        :param ~microcontroller.Pin dm: The data minus pin
        """
        ...
