"""Hardware accelerated external bus access

The I2CDevice and SPIDevice helper classes make managing transaction state on a bus easy.
For example, they manage locking the bus to prevent other concurrent access. For SPI
devices, it manages the chip select and protocol changes such as mode. For I2C, it
manages the device address."""

from __future__ import annotations
