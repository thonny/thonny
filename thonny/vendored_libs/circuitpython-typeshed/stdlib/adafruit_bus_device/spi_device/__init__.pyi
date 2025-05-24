from __future__ import annotations

from typing import Optional

import busio
import digitalio

class SPIDevice:
    """SPI Device Manager"""

    def __init__(
        self,
        spi: busio.SPI,
        chip_select: Optional[digitalio.DigitalInOut] = None,
        *,
        baudrate: int = 100000,
        polarity: int = 0,
        phase: int = 0,
        extra_clocks: int = 0,
    ) -> None:
        """
        Represents a single SPI device and manages locking the bus and the device address.

        :param ~busio.SPI spi: The SPI bus the device is on
        :param ~digitalio.DigitalInOut chip_select: The chip select pin object that implements the DigitalInOut API. ``None`` if a chip select pin is not being used.
        :param bool cs_active_value: Set to true if your device requires CS to be active high. Defaults to false.
        :param int extra_clocks: The minimum number of clock cycles to cycle the bus after CS is high. (Used for SD cards.)

        Example::

            import busio
            import digitalio
            from board import *
            from adafruit_bus_device.spi_device import SPIDevice
            with busio.SPI(SCK, MOSI, MISO) as spi_bus:
                cs = digitalio.DigitalInOut(D10)
                device = SPIDevice(spi_bus, cs)
                bytes_read = bytearray(4)
                # The object assigned to spi in the with statements below
                # is the original spi_bus object. We are using the busio.SPI
                # operations busio.SPI.readinto() and busio.SPI.write().
                with device as spi:
                    spi.readinto(bytes_read)
                # A second transaction
                with device as spi:
                    spi.write(bytes_read)"""
    ...

    def __enter__(self) -> busio.SPI:
        """Starts a SPI transaction by configuring the SPI and asserting chip select."""
        ...

    def __exit__(self) -> None:
        """Ends a SPI transaction by deasserting chip select. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
