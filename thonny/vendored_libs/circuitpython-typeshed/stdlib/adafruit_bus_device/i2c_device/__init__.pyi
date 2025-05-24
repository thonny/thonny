from __future__ import annotations

import busio
from circuitpython_typing import ReadableBuffer, WriteableBuffer

class I2CDevice:
    """I2C Device Manager"""

    def __init__(self, i2c: busio.I2C, device_address: int, probe: bool = True) -> None:
        """Represents a single I2C device and manages locking the bus and the device
        address.

        :param ~busio.I2C i2c: The I2C bus the device is on
        :param int device_address: The 7 bit device address
        :param bool probe: Probe for the device upon object creation, default is true

        Example::

            import busio
            from board import *
            from adafruit_bus_device.i2c_device import I2CDevice
            with busio.I2C(SCL, SDA) as i2c:
                device = I2CDevice(i2c, 0x70)
                bytes_read = bytearray(4)
                with device:
                    device.readinto(bytes_read)
                # A second transaction
                with device:
                    device.write(bytes_read)
        """
    ...

    def __enter__(self) -> I2CDevice:
        """Context manager entry to lock bus."""
        ...

    def __exit__(self) -> None:
        """Automatically unlocks the bus on exit."""
        ...
    import sys

    def readinto(
        self, buffer: WriteableBuffer, *, start: int = 0, end: int = sys.maxsize
    ) -> None:
        """Read into ``buffer`` from the device.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]`` were passed.
        The number of bytes read will be the length of ``buffer[start:end]``.

        :param WriteableBuffer buffer: read bytes into this buffer
        :param int start: beginning of buffer slice
        :param int end: end of buffer slice; if not specified, use ``len(buffer)``
        """
        ...
    import sys

    def write(
        self, buffer: ReadableBuffer, *, start: int = 0, end: int = sys.maxsize
    ) -> None:
        """Write the bytes from ``buffer`` to the device, then transmit a stop bit.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]`` were passed, but without copying the data.
        The number of bytes written will be the length of ``buffer[start:end]``.

        :param ReadableBuffer buffer: write out bytes from this buffer
        :param int start: beginning of buffer slice
        :param int end: end of buffer slice; if not specified, use ``len(buffer)``
        """
        ...
    import sys

    def write_then_readinto(
        self,
        out_buffer: ReadableBuffer,
        in_buffer: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: int = sys.maxsize,
        in_start: int = 0,
        in_end: int = sys.maxsize,
    ) -> None:
        """Write the bytes from ``out_buffer`` to the device, then immediately
        reads into ``in_buffer`` from the device.

        If ``out_start`` or ``out_end`` is provided, then the buffer will be sliced
        as if ``out_buffer[out_start:out_end]`` were passed, but without copying the data.
        The number of bytes written will be the length of ``out_buffer[out_start:out_end]``.

        If ``in_start`` or ``in_end`` is provided, then the input buffer will be sliced
        as if ``in_buffer[in_start:in_end]`` were passed,
        The number of bytes read will be the length of ``out_buffer[in_start:in_end]``.

        :param ReadableBuffer out_buffer: write out bytes from this buffer
        :param WriteableBuffer in_buffer: read bytes into this buffer
        :param int out_start: beginning of ``out_buffer`` slice
        :param int out_end: end of ``out_buffer`` slice; if not specified, use ``len(out_buffer)``
        :param int in_start: beginning of ``in_buffer`` slice
        :param int in_end: end of ``in_buffer slice``; if not specified, use ``len(in_buffer)``
        """
        ...
