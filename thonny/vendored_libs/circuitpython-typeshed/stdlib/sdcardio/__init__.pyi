"""Interface to an SD card via the SPI bus"""

from __future__ import annotations

import busio
import microcontroller
from circuitpython_typing import ReadableBuffer, WriteableBuffer

class SDCard:
    """SD Card Block Interface

    Controls an SD card over SPI.  This built-in module has higher read
    performance than the library adafruit_sdcard, but it is only compatible with
    `busio.SPI`, not `bitbangio.SPI`.  Usually an SDCard object is used
    with ``storage.VfsFat`` to allow file I/O to an SD card."""

    def __init__(
        self, bus: busio.SPI, cs: microcontroller.Pin, baudrate: int = 8000000
    ) -> None:
        """Construct an SPI SD Card object with the given properties

        :param busio.SPI spi: The SPI bus
        :param microcontroller.Pin cs: The chip select connected to the card
        :param int baudrate: The SPI data rate to use after card setup

        Note that during detection and configuration, a hard-coded low baudrate is used.
        Data transfers use the specified baurate (rounded down to one that is supported by
        the microcontroller)

        .. important::
           If the same SPI bus is shared with other peripherals, it is important that
           the SD card be initialized before accessing any other peripheral on the bus.
           Failure to do so can prevent the SD card from being recognized until it is
           powered off or re-inserted.

        Example usage:

        .. code-block:: python

            import os

            import board
            import sdcardio
            import storage

            sd = sdcardio.SDCard(board.SPI(), board.SD_CS)
            vfs = storage.VfsFat(sd)
            storage.mount(vfs, '/sd')
            os.listdir('/sd')"""

    def count(self) -> int:
        """Returns the total number of sectors

        Due to technical limitations, this is a function and not a property.

        :return: The number of 512-byte blocks, as a number"""

    def deinit(self) -> None:
        """Disable permanently.

        :return: None"""

    def readblocks(self, start_block: int, buf: WriteableBuffer) -> None:
        """Read one or more blocks from the card

        :param int start_block: The block to start reading from
        :param ~circuitpython_typing.WriteableBuffer buf: The buffer to write into.  Length must be multiple of 512.

        :return: None"""

    def sync(self) -> None:
        """Ensure all blocks written are actually committed to the SD card

        :return: None"""
        ...

    def writeblocks(self, start_block: int, buf: ReadableBuffer) -> None:
        """Write one or more blocks to the card

        :param int start_block: The block to start writing from
        :param ~circuitpython_typing.ReadableBuffer buf: The buffer to read from.  Length must be multiple of 512.

        :return: None"""
