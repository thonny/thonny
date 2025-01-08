"""Interface to an SD card via the SDIO bus"""

from __future__ import annotations

from typing import Sequence

import microcontroller
from circuitpython_typing import ReadableBuffer, WriteableBuffer

class SDCard:
    """SD Card Block Interface with SDIO

    Controls an SD card over SDIO.  SDIO is a parallel protocol designed
    for SD cards.  It uses a clock pin, a command pin, and 1 or 4
    data pins.  It can be operated at a high frequency such as
    25MHz.  Usually an SDCard object is used with ``storage.VfsFat``
    to allow file I/O to an SD card."""

    def __init__(
        self,
        clock: microcontroller.Pin,
        command: microcontroller.Pin,
        data: Sequence[microcontroller.Pin],
        frequency: int,
    ) -> None:
        """Construct an SDIO SD Card object with the given properties

        :param ~microcontroller.Pin clock: the pin to use for the clock.
        :param ~microcontroller.Pin command: the pin to use for the command.
        :param data: A sequence of pins to use for data.
        :param frequency: The frequency of the bus in Hz

        Example usage:

        .. code-block:: python

            import os

            import board
            import sdioio
            import storage

            sd = sdioio.SDCard(
                clock=board.SDIO_CLOCK,
                command=board.SDIO_COMMAND,
                data=[board.SDIO_DATA],
                frequency=25000000)
            vfs = storage.VfsFat(sd)
            storage.mount(vfs, '/sd')
            os.listdir('/sd')"""
        ...

    def configure(self, frequency: int = 0, width: int = 0) -> None:
        """Configures the SDIO bus.

        :param int frequency: the desired clock rate in Hertz. The actual clock rate may be higher or lower due to the granularity of available clock settings.  Check the `frequency` attribute for the actual clock rate.
        :param int width: the number of data lines to use.  Must be 1 or 4 and must also not exceed the number of data lines at construction

        .. note:: Leaving a value unspecified or 0 means the current setting is kept"""

    def count(self) -> int:
        """Returns the total number of sectors

        Due to technical limitations, this is a function and not a property.

        :return: The number of 512-byte blocks, as a number"""

    def readblocks(self, start_block: int, buf: WriteableBuffer) -> None:
        """Read one or more blocks from the card

        :param int start_block: The block to start reading from
        :param ~circuitpython_typing.WriteableBuffer buf: The buffer to write into.  Length must be multiple of 512.

        :return: None"""

    def writeblocks(self, start_block: int, buf: ReadableBuffer) -> None:
        """Write one or more blocks to the card

        :param int start_block: The block to start writing from
        :param ~circuitpython_typing.ReadableBuffer buf: The buffer to read from.  Length must be multiple of 512.

        :return: None"""
    frequency: int
    """The actual SDIO bus frequency. This may not match the frequency
    requested due to internal limitations."""
    width: int
    """The actual SDIO bus width, in bits"""
    def deinit(self) -> None:
        """Disable permanently.

        :return: None"""

    def __enter__(self) -> SDCard:
        """No-op used by Context Managers.
        Provided by context manager helper."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
