"""Hardware accelerated external bus access

The `busio` module contains classes to support a variety of serial
protocols.

When the microcontroller does not support the behavior in a hardware
accelerated fashion it may internally use a bitbang routine. However, if
hardware support is available on a subset of pins but not those provided,
then a RuntimeError will be raised. Use the `bitbangio` module to explicitly
bitbang a serial protocol on any general purpose pins.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import busio
  from board import *

  i2c = busio.I2C(SCL, SDA)
  print(i2c.scan())
  i2c.deinit()

This example will initialize the the device, run
:py:meth:`~busio.I2C.scan` and then :py:meth:`~busio.I2C.deinit` the
hardware. The last step is optional because CircuitPython automatically
resets hardware after a program finishes."""

class I2C:
    """Two wire serial protocol"""

    def __init__(self, scl: microcontroller.Pin, sda: microcontroller.Pin, *, frequency: int = 400000, timeout: int = 255):

        """I2C is a two-wire protocol for communicating between devices.  At the
        physical level it consists of 2 wires: SCL and SDA, the clock and data
        lines respectively.

        .. seealso:: Using this class directly requires careful lock management.
            Instead, use :class:`~adafruit_bus_device.i2c_device.I2CDevice` to
            manage locks.

        .. seealso:: Using this class to directly read registers requires manual
            bit unpacking. Instead, use an existing driver or make one with
            :ref:`Register <register-module-reference>` data descriptors.

        :param ~microcontroller.Pin scl: The clock pin
        :param ~microcontroller.Pin sda: The data pin
        :param int frequency: The clock frequency in Hertz
        :param int timeout: The maximum clock stretching timeut - (used only for bitbangio.I2C; ignored for busio.I2C)

        .. note:: On the nRF52840, only one I2C object may be created,
           except on the Circuit Playground Bluefruit, which allows two,
           one for the onboard accelerometer, and one for offboard use."""
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

    def scan(self, ) -> Any:

         """Scan all I2C addresses between 0x08 and 0x77 inclusive and return a
         list of those that respond.

         :return: List of device ids on the I2C bus
         :rtype: list"""
         ...

    def try_lock(self, ) -> Any:
        """Attempts to grab the I2C lock. Returns True on success.

        :return: True when lock has been grabbed
        :rtype: bool"""
        ...

    def unlock(self, ) -> Any:
        """Releases the I2C lock."""
        ...

    def readfrom_into(self, address: int, buffer: bytearray, *, start: int = 0, end: int = None) -> Any:
         """Read into ``buffer`` from the slave specified by ``address``.
         The number of bytes read will be the length of ``buffer``.
         At least one byte must be read.

         If ``start`` or ``end`` is provided, then the buffer will be sliced
         as if ``buffer[start:end]``. This will not cause an allocation like
         ``buf[start:end]`` will so it saves memory.

         :param int address: 7-bit device address
         :param bytearray buffer: buffer to write into
         :param int start: Index to start writing at
         :param int end: Index to write up to but not include. Defaults to ``len(buffer)``"""
         ...

    def writeto(self, address: int, buffer: bytearray, *, start: int = 0, end: int = None, stop: bool = True) -> Any:
         """Write the bytes from ``buffer`` to the slave specified by ``address``.
         Transmits a stop bit when stop is True. Setting stop=False is deprecated and stop will be
         removed in CircuitPython 6.x. Use `writeto_then_readfrom` when needing a write, no stop and
         repeated start before a read.

         If ``start`` or ``end`` is provided, then the buffer will be sliced
         as if ``buffer[start:end]``. This will not cause an allocation like
         ``buffer[start:end]`` will so it saves memory.

        Writing a buffer or slice of length zero is permitted, as it can be used
         to poll for the existence of a device.

         :param int address: 7-bit device address
         :param bytearray buffer: buffer containing the bytes to write
         :param int start: Index to start writing from
         :param int end: Index to read up to but not include. Defaults to ``len(buffer)``
         :param bool stop: If true, output an I2C stop condition after the buffer is written.
                           Deprecated. Will be removed in 6.x and act as stop=True."""
         ...

    def writeto_then_readfrom(self, address: int, out_buffer: bytearray, in_buffer: bytearray, *, out_start: int = 0, out_end: int = None, in_start: int = 0, in_end: int = None) -> Any:
         """Write the bytes from ``out_buffer`` to the slave specified by ``address``, generate no stop
         bit, generate a repeated start and read into ``in_buffer``. ``out_buffer`` and
         ``in_buffer`` can be the same buffer because they are used sequentially.

        If ``start`` or ``end`` is provided, then the corresponding buffer will be sliced
         as if ``buffer[start:end]``. This will not cause an allocation like ``buf[start:end]``
         will so it saves memory.

         :param int address: 7-bit device address
         :param bytearray out_buffer: buffer containing the bytes to write
         :param bytearray in_buffer: buffer to write into
         :param int out_start: Index to start writing from
         :param int out_end: Index to read up to but not include. Defaults to ``len(buffer)``
         :param int in_start: Index to start writing at
         :param int in_end: Index to write up to but not include. Defaults to ``len(buffer)``"""
         ...

class OneWire:
    """Lowest-level of the Maxim OneWire protocol"""

    def __init__(self, pin: microcontroller.Pin):
        """(formerly Dallas Semi) OneWire protocol.

        Protocol definition is here: https://www.maximintegrated.com/en/app-notes/index.mvp/id/126

        .. class:: OneWire(pin)

          Create a OneWire object associated with the given pin. The object
          implements the lowest level timing-sensitive bits of the protocol.

          :param ~microcontroller.Pin pin: Pin connected to the OneWire bus

          Read a short series of pulses::

            import busio
            import board

            onewire = busio.OneWire(board.D7)
            onewire.reset()
            onewire.write_bit(True)
            onewire.write_bit(False)
            print(onewire.read_bit())"""
        ...

    def deinit(self, ) -> Any:
        """Deinitialize the OneWire bus and release any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def reset(self, ) -> Any:
        """Reset the OneWire bus and read presence

        :returns: False when at least one device is present
        :rtype: bool"""
        ...

    def read_bit(self, ) -> Any:
        """Read in a bit

        :returns: bit state read
        :rtype: bool"""
        ...

    def write_bit(self, value: Any) -> Any:
        """Write out a bit based on value."""
        ...

class SPI:
    """A 3-4 wire serial protocol

    SPI is a serial protocol that has exclusive pins for data in and out of the
    master.  It is typically faster than :py:class:`~busio.I2C` because a
    separate pin is used to control the active slave rather than a transitted
    address. This class only manages three of the four SPI lines: `!clock`,
    `!MOSI`, `!MISO`. Its up to the client to manage the appropriate slave
    select line. (This is common because multiple slaves can share the `!clock`,
    `!MOSI` and `!MISO` lines and therefore the hardware.)"""

    def __init__(self, clock: microcontroller.Pin, MOSI: microcontroller.Pin = None, MISO: microcontroller.Pin = None):

        """Construct an SPI object on the given pins.

        ..note:: The SPI peripherals allocated in order of desirability, if possible,
           such as highest speed and not shared use first. For instance, on the nRF52840,
           there is a single 32MHz SPI peripheral, and multiple 8MHz peripherals,
           some of which may also be used for I2C. The 32MHz SPI peripheral is returned
           first, then the exclusive 8MHz SPI peripheral, and finally the shared 8MHz
           peripherals.

        .. seealso:: Using this class directly requires careful lock management.
            Instead, use :class:`~adafruit_bus_device.spi_device.SPIDevice` to
            manage locks.

        .. seealso:: Using this class to directly read registers requires manual
            bit unpacking. Instead, use an existing driver or make one with
            :ref:`Register <register-module-reference>` data descriptors.

        :param ~microcontroller.Pin clock: the pin to use for the clock.
        :param ~microcontroller.Pin MOSI: the Master Out Slave In pin.
        :param ~microcontroller.Pin MISO: the Master In Slave Out pin."""
        ...

    def deinit(self, ) -> Any:
        """Turn off the SPI bus."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers.
        Provided by context manager helper."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def configure(self, *, baudrate: int = 100000, polarity: int = 0, phase: int = 0, bits: int = 8) -> Any:
        """Configures the SPI bus. The SPI object must be locked.

        :param int baudrate: the desired clock rate in Hertz. The actual clock rate may be higher or lower
          due to the granularity of available clock settings.
          Check the `frequency` attribute for the actual clock rate.
        :param int polarity: the base state of the clock line (0 or 1)
        :param int phase: the edge of the clock that data is captured. First (0)
          or second (1). Rising or falling depends on clock polarity.
        :param int bits: the number of bits per word

       .. note:: On the SAMD21, it is possible to set the baudrate to 24 MHz, but that
           speed is not guaranteed to work. 12 MHz is the next available lower speed, and is
           within spec for the SAMD21.

        .. note:: On the nRF52840, these baudrates are available: 125kHz, 250kHz, 1MHz, 2MHz, 4MHz,
          and 8MHz.
          If you pick a a baudrate other than one of these, the nearest lower
          baudrate will be chosen, with a minimum of 125kHz.
          Two SPI objects may be created, except on the Circuit Playground Bluefruit,
          which allows only one (to allow for an additional I2C object)."""
        ...

    def try_lock(self, ) -> Any:
        """Attempts to grab the SPI lock. Returns True on success.

        :return: True when lock has been grabbed
        :rtype: bool"""
        ...

    def unlock(self, ) -> Any:
        """Releases the SPI lock."""
        ...

    def write(self, buffer: bytearray, *, start: Any = 0, end: int = None) -> Any:
        """Write the data contained in ``buffer``. The SPI object must be locked.
        If the buffer is empty, nothing happens.

        :param bytearray buffer: Write out the data in this buffer
        :param int start: Start of the slice of ``buffer`` to write out: ``buffer[start:end]``
        :param int end: End of the slice; this index is not included. Defaults to ``len(buffer)``"""
        ...

    def readinto(self, buffer: bytearray, *, start: Any = 0, end: int = None, write_value: int = 0) -> Any:
        """Read into ``buffer`` while writing ``write_value`` for each byte read.
        The SPI object must be locked.
        If the number of bytes to read is 0, nothing happens.

        :param bytearray buffer: Read data into this buffer
        :param int start: Start of the slice of ``buffer`` to read into: ``buffer[start:end]``
        :param int end: End of the slice; this index is not included. Defaults to ``len(buffer)``
        :param int write_value: Value to write while reading. (Usually ignored.)"""
        ...

    def write_readinto(self, buffer_out: bytearray, buffer_in: bytearray, *, out_start: Any = 0, out_end: int = None, in_start: Any = 0, in_end: int = None) -> Any:
        """Write out the data in ``buffer_out`` while simultaneously reading data into ``buffer_in``.
        The SPI object must be locked.
        The lengths of the slices defined by ``buffer_out[out_start:out_end]`` and ``buffer_in[in_start:in_end]``
        must be equal.
        If buffer slice lengths are both 0, nothing happens.

        :param bytearray buffer_out: Write out the data in this buffer
        :param bytearray buffer_in: Read data into this buffer
        :param int out_start: Start of the slice of buffer_out to write out: ``buffer_out[out_start:out_end]``
        :param int out_end: End of the slice; this index is not included. Defaults to ``len(buffer_out)``
        :param int in_start: Start of the slice of ``buffer_in`` to read into: ``buffer_in[in_start:in_end]``
        :param int in_end: End of the slice; this index is not included. Defaults to ``len(buffer_in)``"""
        ...

    frequency: Any = ...
    """The actual SPI bus frequency. This may not match the frequency requested
    due to internal limitations."""

class UART:
    """A bidirectional serial protocol"""
    def __init__(self, tx: microcontroller.Pin, rx: microcontroller.Pin, *, baudrate: int = 9600, bits: int = 8, parity: Parity = None, stop: int = 1, timeout: float = 1, receiver_buffer_size: int = 64):
        """A common bidirectional serial protocol that uses an an agreed upon speed
        rather than a shared clock line.

        :param ~microcontroller.Pin tx: the pin to transmit with, or ``None`` if this ``UART`` is receive-only.
        :param ~microcontroller.Pin rx: the pin to receive on, or ``None`` if this ``UART`` is transmit-only.
        :param ~microcontroller.Pin rts: the pin for rts, or ``None`` if rts not in use.
        :param ~microcontroller.Pin cts: the pin for cts, or ``None`` if cts not in use.
        :param ~microcontroller.Pin rs485_dir: the pin for rs485 direction setting, or ``None`` if rs485 not in use.
        :param bool rs485_invert: set to invert the sense of the rs485_dir pin.
        :param int baudrate: the transmit and receive speed.
        :param int bits:  the number of bits per byte, 7, 8 or 9.
        :param Parity parity:  the parity used for error checking.
        :param int stop:  the number of stop bits, 1 or 2.
        :param float timeout:  the timeout in seconds to wait for the first character and between subsequent characters when reading. Raises ``ValueError`` if timeout >100 seconds.
        :param int receiver_buffer_size: the character length of the read buffer (0 to disable). (When a character is 9 bits the buffer will be 2 * receiver_buffer_size bytes.)

        *New in CircuitPython 4.0:* ``timeout`` has incompatibly changed units from milliseconds to seconds.
        The new upper limit on ``timeout`` is meant to catch mistaken use of milliseconds."""
        ...

    def deinit(self, ) -> Any:
        """Deinitialises the UART and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def read(self, nbytes: Any = None) -> Any:
        """Read characters.  If ``nbytes`` is specified then read at most that many
        bytes. Otherwise, read everything that arrives until the connection
        times out. Providing the number of bytes expected is highly recommended
        because it will be faster.

        :return: Data read
        :rtype: bytes or None"""
        ...

    def readinto(self, buf: Any) -> Any:
        """Read bytes into the ``buf``. Read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)

        *New in CircuitPython 4.0:* No length parameter is permitted."""
        ...

    def readline(self, ) -> Any:
        """Read a line, ending in a newline character.

        :return: the line read
        :rtype: int or None"""
        ...

    def write(self, buf: Any) -> Any:
        """Write the buffer of bytes to the bus.

      *New in CircuitPython 4.0:* ``buf`` must be bytes, not a string.

        :return: the number of bytes written
        :rtype: int or None"""
        ...

    baudrate: Any = ...
    """The current baudrate."""

    in_waiting: Any = ...
    """The number of bytes in the input buffer, available to be read"""

    timeout: Any = ...
    """The current timeout, in seconds (float)."""

    def reset_input_buffer(self, ) -> Any: ...
    """Discard any unread characters in the input buffer."""

class Parity:
    """Enum-like class to define the parity used to verify correct data transfer."""

    ODD: Any = ...
    """Total number of ones should be odd."""

    EVEN: Any = ...
    """Total number of ones should be even."""

