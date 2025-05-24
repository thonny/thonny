"""Two wire serial protocol target

In many cases, i2c is used by a controller to retrieve (or send) to a peripheral (target). It is also possible
for a device to act as a target for another controller.  However, a device can only be a controller or a target on
an I2C bus (although many devices now support multiple I2C busses).

.. note::
   `I2CTarget` takes a list of addresses, but not all devices support this feature

Example of emulating a simple device that can only handle single writes and reads::

   import board
   from i2ctarget import I2CTarget

   import adafruit_logging as logging

   logger = logging.getLogger('i2ctarget')
   logger.setLevel(logging.INFO)
   logger.addHandler(logging.StreamHandler())

   logger.info("\\n\\ncode starting...")

   # initialize an I2C target with a device address of 0x40
   with I2CTarget(board.SCL, board.SDA, (0x40,)) as device:

       while True:
           # check if there's a pending device request
           i2c_target_request = device.request()

           if not i2c_target_request:
               # no request is pending
               continue

           # `with` invokes I2CTargetRequest's functions to handle the necessary opening and closing of a request
           with i2c_target_request:

               # the address associated with the request
               address = i2c_target_request.address

               if i2c_target_request.is_read:
                   logger.info(f"read request to address '0x{address:02x}'")

                   # for our emulated device, return a fixed value for the request
                   buffer = bytes([0xaa])
                   i2c_target_request.write(buffer)
               else:
                   # transaction is a write request
                   data = i2c_target_request.read(1)
                   logger.info(f"write request to address 0x{address:02x}: {data}")
                   # for our emulated device, writes have no effect

This example creates an I2C target device that can be accessed via another device as an I2C controller::

       import busio
       import board
       i2c = busio.I2C(board.SCL, board.SDA)

       # perform a single read
       while not i2c.try_lock():
           pass
       buffer = bytearray(1)
       i2c.readfrom_into(0x40, buffer)
       print(f"device responded with {buffer}")
       i2c.unlock()

       # perform a single write
       while not i2c.try_lock():
           pass
       buffer = bytearray(1)
       buffer[0] = 0x12
       i2c.writeto(0x40, buffer)
       print(f"wrote {buffer} to device")
       i2c.unlock()

Typically, i2c devices support writes and reads to/from multiple register indices as in this example    ::

   import board
   from i2ctarget import I2CTarget

   import adafruit_logging as logging

   logger = logging.getLogger('i2ctarget')
   logger.setLevel(logging.INFO)
   logger.addHandler(logging.StreamHandler())

   # emulate a target with 16 registers
   regs = [0] * 16
   register_index = None

   logger.info("\\n\\ncode starting...")

   # initialize an I2C target with a device address of 0x40
   with I2CTarget(board.SCL, board.SDA, (0x40,)) as device:

       while True:
           # check if there's a pending device request
           i2c_target_request = device.request()

           if not i2c_target_request:
               # no request is pending
               continue

           # work with the i2c request
           with i2c_target_request:

               if not i2c_target_request.is_read:
                   # a write request

                   # bytearray contains the request's first byte, the register's index
                   index = i2c_target_request.read(1)[0]

                   # bytearray containing the request's second byte, the data
                   data = i2c_target_request.read(1)

                   # if the request doesn't have a second byte, this is read transaction
                   if not data:

                       # since we're only emulating 16 registers, read from a larger address is an error
                       if index > 15:
                           logger.error(f"write portion of read transaction has invalid index {index}")
                           continue

                       logger.info(f"write portion of read transaction, set index to {index}'")
                       register_index = index
                       continue

                   # since we're only emulating 16 registers, writing to a larger address is an error
                   if index > 15:
                       logger.error(f"write request to incorrect index {index}")
                       continue

                   logger.info(f"write request to index {index}: {data}")
                   regs[index] = data[0]
               else:
                   # our emulated device requires a read to be part of a full write-then-read transaction
                   if not i2c_target_request.is_restart:
                       logger.warning(f"read request without first writing is not supported")
                       # still need to respond, but result data is not defined
                       i2c_target_request.write(bytes([0xff]))
                       register_index = None
                       continue

                   # the single read transaction case is covered above, so we should always have a valid index
                   assert(register_index is not None)

                   # the write-then-read to an invalid address is covered above,
                   #   but if this is a restarted read, index might be out of bounds so need to check
                   if register_index > 16:
                       logger.error(f"restarted read yielded an unsupported index")
                       i2c_target_request.write(bytes([0xff]))
                       register_index = None
                       continue

                   # retrieve the data from our register file and respond
                   data = regs[register_index]
                   logger.info(f"read request from index {register_index}: {data}")
                   i2c_target_request.write(bytes([data]))

                   # in our emulated device, a single read transaction is covered above
                   #   so any subsequent restarted read gets the value at the next index
                   assert(i2c_target_request.is_restart is True)
                   register_index += 1

This second example creates I2C target device that can be accessed via another device as an I2C controller::

   import busio
   import board
   i2c = busio.I2C(board.SCL, board.SDA)

   # perform a write transaction
   while not i2c.try_lock():
       pass
   buffer = bytearray(2)
   buffer[0] = 0x0b  # the register index
   buffer[1] = 0xa1  # the value
   i2c.writeto(0x40, buffer)
   print(f"wrote {buffer} to device")
   i2c.unlock()

   # perform a full read transaction (write-then-read)
   while not i2c.try_lock():
       pass
   index_buffer = bytearray(1)
   index_buffer[0] = 0x0b
   read_buffer = bytearray(1)
   i2c.writeto_then_readfrom(0x40, index_buffer, read_buffer)
   print(f"read from device index {index_buffer}: {read_buffer}")
   i2c.unlock()

Or accessed from Linux like this::

   $ i2cget -y 1 0x40 0x0b
   0xff
   $ i2cset -y 1 0x40 0x0b 0xa1
   $ i2cget -y 1 0x40 0x01
   0xa1

.. warning::
   I2CTarget makes use of clock stretching in order to slow down the host.
   Make sure the I2C host supports this.

   Raspberry Pi 3 and below, in particular, do not support this with its I2C hw block.
   This can be worked around by using the ``i2c-gpio`` bit banging driver.
   Since the RPi firmware uses the hw i2c, it's not possible to emulate a HAT eeprom."""

from __future__ import annotations

from typing import Sequence

import i2ctarget
import microcontroller
from circuitpython_typing import ReadableBuffer

class I2CTarget:
    """Two wire serial protocol target"""

    def __init__(
        self,
        scl: microcontroller.Pin,
        sda: microcontroller.Pin,
        addresses: Sequence[int],
        smbus: bool = False,
    ) -> None:
        """I2C is a two-wire protocol for communicating between devices.
        This implements the target (peripheral, sensor, secondary) side.

        :param ~microcontroller.Pin scl: The clock pin
        :param ~microcontroller.Pin sda: The data pin
        :param addresses: The I2C addresses to respond to (how many is hardware dependent).
        :type addresses: list[int]
        :param bool smbus: Use SMBUS timings if the hardware supports it"""
        ...

    def deinit(self) -> None:
        """Releases control of the underlying hardware so other classes can use it."""
        ...

    def __enter__(self) -> I2CTarget:
        """No-op used in Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware on context exit. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def request(self, *, timeout: float = -1) -> I2CTargetRequest:
        """Wait for an I2C request.

        :param float timeout: Timeout in seconds. Zero means wait forever, a negative value means check once
        :return: I2CTargetRequest or None if timeout=-1 and there's no request
        :rtype: ~i2ctarget.I2CTargetRequest"""

class I2CTargetRequest:
    def __init__(
        self, target: i2ctarget.I2CTarget, address: int, is_read: bool, is_restart: bool
    ) -> None:
        """Information about an I2C transfer request
        This cannot be instantiated directly, but is returned by :py:meth:`I2CTarget.request`.

        :param target: The I2CTarget object receiving this request
        :param address: I2C address
        :param is_read: True if the main target is requesting data
        :param is_restart: Repeated Start Condition"""

    def __enter__(self) -> I2CTargetRequest:
        """No-op used in Context Managers."""
        ...

    def __exit__(self) -> None:
        """Close the request."""
        ...
    address: int
    """The I2C address of the request."""
    is_read: bool
    """The I2C main controller is reading from this target."""
    is_restart: bool
    """Is Repeated Start Condition."""

    def read(self, n: int = -1, ack: bool = True) -> bytearray:
        """Read data.
        If ack=False, the caller is responsible for calling :py:meth:`I2CTargetRequest.ack`.

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
        Use together with :py:meth:`I2CTargetRequest.read` ack=False.

        :param ack: Whether to send an ACK or NACK"""
        ...
