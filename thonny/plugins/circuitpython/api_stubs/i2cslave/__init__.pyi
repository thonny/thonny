"""Two wire serial protocol slave

The `i2cslave` module contains classes to support a I2C slave.

Example emulating 2 devices::

  import board
  from i2cslave import I2CSlave

  regs = [0] * 16
  index = 0

  with I2CSlave(board.SCL, board.SDA, (0x40, 0x41)) as slave:
      while True:
          r = slave.request()
          if not r:
              # Maybe do some housekeeping
              continue
          with r:  # Closes the transfer if necessary by sending a NACK or feeding the master dummy bytes
              if r.address == 0x40:
                  if not r.is_read:  # Master write which is Slave read
                      b = r.read(1)
                      if not b or b[0] > 15:
                          break
                      index = b[0]
                      b = r.read(1)
                      if b:
                          regs[index] = b[0]
                  elif r.is_restart:  # Combined transfer: This is the Master read message
                      n = r.write(bytes([regs[index]]))
                  #else:
                      # A read transfer is not supported in this example
                      # If the Master tries, it will get 0xff byte(s) by the ctx manager (r.close())
              elif r.address == 0x41:
                  if not r.is_read:
                      b = r.read(1)
                      if b and b[0] == 0xde:
                          # do something
                          pass

This example sets up an I2C slave that can be accessed from Linux like this::

  $ i2cget -y 1 0x40 0x01
  0x00
  $ i2cset -y 1 0x40 0x01 0xaa
  $ i2cget -y 1 0x40 0x01
  0xaa

.. warning::
   I2CSlave makes use of clock stretching in order to slow down the master.
   Make sure the I2C master supports this.

   Raspberry Pi in particular does not support this with its I2C hw block.
   This can be worked around by using the ``i2c-gpio`` bit banging driver.
   Since the RPi firmware uses the hw i2c, it's not possible to emulate a HAT eeprom."""

class I2CSlave:
    """Two wire serial protocol slave"""

    def __init__(self, scl: microcontroller.Pin, sda: microcontroller.Pin, addresses: tuple, smbus: bool = False):
        """I2C is a two-wire protocol for communicating between devices.
        This implements the slave side.

        :param ~microcontroller.Pin scl: The clock pin
        :param ~microcontroller.Pin sda: The data pin
        :param tuple addresses: The I2C addresses to respond to (how many is hw dependent).
        :param bool smbus: Use SMBUS timings if the hardware supports it"""
        ...

    def deinit(self, ) -> Any:
        """Releases control of the underlying hardware so other classes can use it."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used in Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware on context exit. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def request(self, timeout: float = -1) -> Any:
        """Wait for an I2C request from a master.

        :param float timeout: Timeout in seconds. Zero means wait forever, a negative value means check once
        :return: I2C Slave Request or None if timeout=-1 and there's no request
        :rtype: ~i2cslave.I2CSlaveRequest"""

class I2CSlaveRequest:

    def __init__(self, slave: i2cslave.I2CSlave, address: int, is_read: bool, is_restart: bool):
        """I2C transfer request from a master.
        This cannot be instantiated directly, but is returned by :py:meth:`I2CSlave.request`.

        :param slave: The I2C Slave receiving this request
        :param address: I2C address
        :param is_read: I2C Master read request
        :param is_restart: Repeated Start Condition"""

    def __enter__(self, ) -> Any:
        """No-op used in Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Close the request."""
        ...

    address: int = ...
    """The I2C address of the request."""

    is_read: bool = ...
    """The I2C master is reading from the device."""

    is_restart: bool = ...
    """Is Repeated Start Condition."""

    def read(self, n: int = -1, ack: bool = True) -> bytearray:
        """Read data.
        If ack=False, the caller is responsible for calling :py:meth:`I2CSlaveRequest.ack`.

        :param n: Number of bytes to read (negative means all)
        :param ack: Whether or not to send an ACK after the n'th byte
        :return: Bytes read"""
        ...

    def write(self, buffer: bytearray) -> int:
        """Write the data contained in buffer.

        :param buffer: Write out the data in this buffer
        :return: Number of bytes written"""
        ...

    def ack(self, ack: bool = True) -> Any:
        """Acknowledge or Not Acknowledge last byte received.
        Use together with :py:meth:`I2CSlaveRequest.read` ack=False.

        :param ack: Whether to send an ACK or NACK"""
        ...

