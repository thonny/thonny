"""USB Core

This is a subset of the PyUSB core module.
"""

from __future__ import annotations

import array

from circuitpython_typing import ReadableBuffer

class USBError(OSError):
    """Catchall exception for USB related errors."""

    ...

class USBTimeoutError(USBError):
    """Raised when a USB transfer times out."""

    ...

def find(find_all=False, *, idVendor=None, idProduct=None):
    """Find the first device that matches the given requirements or, if
    find_all is True, return a generator of all matching devices.

    Returns None if no device matches.
    """

class Device:
    def __init__(self) -> None:
        """User code cannot create Device objects. Instead, get them from
        `usb.core.find`.
        """
        ...
    idVendor: int
    """The USB vendor ID of the device"""

    idProduct: int
    """The USB product ID of the device"""

    serial_number: str
    """The USB device's serial number string."""

    product: str
    """The USB device's product string."""

    manufacturer: str
    """The USB device's manufacturer string."""

    def write(self, endpoint: int, data: ReadableBuffer, timeout=None) -> int:
        """Write data to a specific endpoint on the device.

        :param int endpoint: the bEndpointAddress you want to communicate with.
        :param ReadableBuffer data: the data to send
        :param int timeout: Time to wait specified in milliseconds. (Different from most CircuitPython!)
        :returns: the number of bytes written
        """
        ...
    def read(self, endpoint: int, size_or_buffer: array.array, timeout=None) -> int:
        """Read data from the endpoint.

        :param int endpoint: the bEndpointAddress you want to communicate with.
        :param array.array size_or_buffer: the array to read data into. PyUSB also allows size but CircuitPython only support array to force deliberate memory use.
        :param int timeout: Time to wait specified in milliseconds. (Different from most CircuitPython!)
        :returns: the number of bytes read
        """
        ...
    def ctrl_transfer(
        self,
        bmRequestType,
        bRequest,
        wValue=0,
        wIndex=0,
        data_or_wLength: array.array = None,
        timeout=None,
    ) -> int:
        """Do a control transfer on the endpoint 0. The parameters bmRequestType,
        bRequest, wValue and wIndex are the same of the USB Standard Control
        Request format.

        Control requests may or may not have a data payload to write/read.
        In cases which it has, the direction bit of the bmRequestType
        field is used to infer the desired request direction.

        For host to device requests (OUT), data_or_wLength parameter is
        the data payload to send, and it must be a sequence type convertible
        to an array object. In this case, the return value is the number
        of bytes written in the data payload.

        For device to host requests (IN), data_or_wLength is an array
        object which the data will be read to, and the return value is the
        number of bytes read.
        """
        ...
    def is_kernel_driver_active(self, interface: int) -> bool:
        """Determine if CircuitPython is using the interface. If it is, the
        object will be unable to perform I/O.

        :param int interface: the device interface number to check
        """
        ...
    def detach_kernel_driver(self, interface: int):
        """Stop CircuitPython from using the interface. If successful, you
        will then be able to perform I/O. CircuitPython will automatically
        re-start using the interface on reload.

        :param int interface: the device interface number to stop CircuitPython on
        """
        ...
    def attach_kernel_driver(self, interface: int):
        """Allow CircuitPython to use the interface if it wants to.

        :param int interface: the device interface number to allow CircuitPython to use
        """
        ...
