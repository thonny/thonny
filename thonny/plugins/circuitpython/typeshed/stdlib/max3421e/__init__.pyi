"""Provide USB host via a connected MAX3421E chip.

Here is how to test with the MAX3421E featherwing:

.. code-block:: python

   import board
   import max3421e
   import time
   import usb

   spi = board.SPI()
   cs = board.D10
   irq = board.D9

   host_chip = max3421e.Max3421E(spi, chip_select=cs, irq=irq)

   while True:
      print("Finding devices:")
      for device in usb.core.find(find_all=True):
          print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
      time.sleep(5)

"""

from __future__ import annotations

import busio
import microcontroller

class Max3421E:
    """Interface with a Max3421E usb host chip."""

    def __init__(
        self,
        spi_bus: busio.SPI,
        *,
        chip_select: microcontroller.Pin,
        irq: microcontroller.Pin,
        baudrate: int = 26000000,
    ) -> None:
        """Create a Max3421E object associated with the given pins.

        Although this object isn't used directly for USB host (the `usb` module is).
        You must keep it alive in memory. When deinit, it will shut down USB host functionality.

        :param busio.SPI spi_bus: The SPI bus that make up the clock and data lines
        :param microcontroller.Pin chip_select: Chip select pin
        :param microcontroller.Pin irq: Interrupt pin
        :param int baudrate: Maximum baudrate to talk to the Max chip in Hz"""
        ...

    def deinit(self) -> None:
        """Shuts down USB host functionality and releases chip_select and irq pins."""
        ...
