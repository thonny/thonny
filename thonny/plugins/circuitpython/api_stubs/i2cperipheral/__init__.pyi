"""Two wire serial protocol peripheral

The `i2cperipheral` module contains classes to support an I2C peripheral.

Example emulating a peripheral with 2 addresses (read and write)::

  import board
  from i2cperipheral import I2CPeripheral

  regs = [0] * 16
  index = 0

  with I2CPeripheral(board.SCL, board.SDA, (0x40, 0x41)) as device:
      while True:
          r = device.request()
          if not r:
              # Maybe do some housekeeping
              continue
          with r:  # Closes the transfer if necessary by sending a NACK or feeding dummy bytes
              if r.address == 0x40:
                  if not r.is_read:  # Main write which is Selected read
                      b = r.read(1)
                      if not b or b[0] > 15:
                          break
                      index = b[0]
                      b = r.read(1)
                      if b:
                          regs[index] = b[0]
                  elif r.is_restart:  # Combined transfer: This is the Main read message
                      n = r.write(bytes([regs[index]]))
                  #else:
                      # A read transfer is not supported in this example
                      # If the microcontroller tries, it will get 0xff byte(s) by the ctx manager (r.close())
              elif r.address == 0x41:
                  if not r.is_read:
                      b = r.read(1)
                      if b and b[0] == 0xde:
                          # do something
                          pass

This example sets up an I2C device that can be accessed from Linux like this::

  $ i2cget -y 1 0x40 0x01
  0x00
  $ i2cset -y 1 0x40 0x01 0xaa
  $ i2cget -y 1 0x40 0x01
  0xaa

.. warning::
   I2CPeripheral makes use of clock stretching in order to slow down
   the host.
   Make sure the I2C host supports this.

   Raspberry Pi in particular does not support this with its I2C hw block.
   This can be worked around by using the ``i2c-gpio`` bit banging driver.
   Since the RPi firmware uses the hw i2c, it's not possible to emulate a HAT eeprom."""

from __future__ import annotations

from typing import Sequence

import i2cperipheral
import microcontroller
from circuitpython_typing import ReadableBuffer

class I2CPeripheral:
    """Two wire serial protocol peripheral"""

    def __init__(
        self,
        scl: microcontroller.Pin,
        sda: microcontroller.Pin,
        addresses: Sequence[int],
        smbus: bool = False,
    ) -> None:
        """I2C is a two-wire protocol for communicating between devices.
        This implements the peripheral (sensor, secondary) side.

        :param ~microcontroller.Pin scl: The clock pin
        :param ~microcontroller.Pin sda: The data pin
        :param addresses: The I2C addresses to respond to (how many is hw dependent).
        :type addresses: list[int]
        :param bool smbus: Use SMBUS timings if the hardware supports it"""
        ...
    def deinit(self) -> None:
        """Releases control of the underlying hardware so other classes can use it."""
        ...
    def __enter__(self) -> I2CPeripheral:
        """No-op used in Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware on context exit. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def request(self, timeout: float = -1) -> I2CPeripheralRequest:
        """Wait for an I2C request.

        :param float timeout: Timeout in seconds. Zero means wait forever, a negative value means check once
        :return: I2C Slave Request or None if timeout=-1 and there's no request
        :rtype: ~i2cperipheral.I2CPeripheralRequest"""

class I2CPeripheralRequest:
    def __init__(
        self,
        peripheral: i2cperipheral.I2CPeripheral,
        address: int,
        is_read: bool,
        is_restart: bool,
    ) -> None:
        """Information about an I2C transfer request
        This cannot be instantiated directly, but is returned by :py:meth:`I2CPeripheral.request`.

        :param peripheral: The I2CPeripheral object receiving this request
        :param address: I2C address
        :param is_read: True if the main peripheral is requesting data
        :param is_restart: Repeated Start Condition"""
    def __enter__(self) -> I2CPeripheralRequest:
        """No-op used in Context Managers."""
        ...
    def __exit__(self) -> None:
        """Close the request."""
        ...
    address: int
    """The I2C address of the request."""

    is_read: bool
    """The I2C main controller is reading from this peripheral."""

    is_restart: bool
    """Is Repeated Start Condition."""

    def read(self, n: int = -1, ack: bool = True) -> bytearray:
        """Read data.
        If ack=False, the caller is responsible for calling :py:meth:`I2CPeripheralRequest.ack`.

        :param n: Number of bytes to read (negative means all)
        :param ack: Whether or not to send an ACK after the n'th byte
        :return: Bytes read"""
        ...
    def write(self, buffer: ReadableBuffer) -> int:
        """Write the data contained in buffer.

        :param ~circuitpython_typing.ReadableBuffer buffer: Write out the data in this buffer
        :return: Number of bytes written"""
        ...
    def ack(self, ack: bool = True) -> None:
        """Acknowledge or Not Acknowledge last byte received.
        Use together with :py:meth:`I2CPeripheralRequest.read` ack=False.

        :param ack: Whether to send an ACK or NACK"""
        ...
