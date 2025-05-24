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
  i2c.try_lock()
  print(i2c.scan())
  i2c.unlock()
  i2c.deinit()

This example will initialize the the device, lock the I2C bus, run
:py:meth:`~busio.I2C.scan`, unlock the bus,
and then :py:meth:`~busio.I2C.deinit` the hardware.
The last step is optional because CircuitPython automatically
resets hardware after a program finishes.

Note that drivers will typically handle communication if provided the bus
instance (such as ``busio.I2C(board.SCL, board.SDA)``), and that many of
the methods listed here are lower level functionalities that are needed
for working with custom drivers.

Tutorial for I2C and SPI:
https://learn.adafruit.com/circuitpython-basics-i2c-and-spi

Tutorial for UART:
https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial

.. jinja
"""

from __future__ import annotations

from typing import List, Optional

import microcontroller
from circuitpython_typing import ReadableBuffer, WriteableBuffer

class I2C:
    """Two wire serial protocol"""

    def __init__(
        self,
        scl: microcontroller.Pin,
        sda: microcontroller.Pin,
        *,
        frequency: int = 100000,
        timeout: int = 255,
    ) -> None:
        """I2C is a two-wire protocol for communicating between devices.  At the
        physical level it consists of 2 wires: SCL and SDA, the clock and data
        lines respectively.

        .. seealso:: Using this class directly requires careful lock management.
            Instead, use :class:`~adafruit_bus_device.I2CDevice` to
            manage locks.

        .. seealso:: Using this class to directly read registers requires manual
            bit unpacking. Instead, use an existing driver or make one with
            :ref:`Register <register-module-reference>` data descriptors.

        .. seealso:: This class provides an I2C controller, which controls I2C targets (peripherals).
            To act as an I2C target, use `i2ctarget.I2CTarget`.

        :param ~microcontroller.Pin scl: The clock pin
        :param ~microcontroller.Pin sda: The data pin
        :param int frequency: The clock frequency in Hertz
        :param int timeout: The maximum clock stretching timeout - (used only for
            :class:`bitbangio.I2C`; ignored for :class:`busio.I2C`)
        """
        ...

    def deinit(self) -> None:
        """Releases control of the underlying hardware so other classes can use it."""
        ...

    def __enter__(self) -> I2C:
        """No-op used in Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware on context exit. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def probe(self, address: int) -> List[int]:
        """Check if a device at the specified address responds.

        :param int address: 7-bit device address
        :return: ``True`` if a device at ``address`` responds; ``False`` otherwise
        :rtype: bool"""
        ...

    def scan(self) -> List[int]:
        """Scan all I2C addresses between 0x08 and 0x77 inclusive and return a
        list of those that respond.

        :return: List of device ids on the I2C bus
        :rtype: list"""
        ...

    def try_lock(self) -> bool:
        """Attempts to grab the I2C lock. Returns True on success.

        :return: True when lock has been grabbed
        :rtype: bool"""
        ...

    def unlock(self) -> None:
        """Releases the I2C lock."""
        ...
    import sys

    def readfrom_into(
        self,
        address: int,
        buffer: WriteableBuffer,
        *,
        start: int = 0,
        end: int = sys.maxsize,
    ) -> None:
        """Read into ``buffer`` from the device selected by ``address``.
        At least one byte must be read.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]`` were passed, but without copying the data.
        The number of bytes read will be the length of ``buffer[start:end]``.

        :param int address: 7-bit device address
        :param WriteableBuffer buffer: buffer to write into
        :param int start: beginning of buffer slice
        :param int end: end of buffer slice; if not specified, use ``len(buffer)``"""
        ...
    import sys

    def writeto(
        self,
        address: int,
        buffer: ReadableBuffer,
        *,
        start: int = 0,
        end: int = sys.maxsize,
    ) -> None:
        """Write the bytes from ``buffer`` to the device selected by ``address`` and
        then transmit a stop bit.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]`` were passed, but without copying the data.
        The number of bytes written will be the length of ``buffer[start:end]``.

        Writing a buffer or slice of length zero is permitted, as it can be used
        to poll for the existence of a device.

        :param int address: 7-bit device address
        :param ReadableBuffer buffer: buffer containing the bytes to write
        :param int start: beginning of buffer slice
        :param int end: end of buffer slice; if not specified, use ``len(buffer)``
        """
        ...
    import sys

    def writeto_then_readfrom(
        self,
        address: int,
        out_buffer: ReadableBuffer,
        in_buffer: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: int = sys.maxsize,
        in_start: int = 0,
        in_end: int = sys.maxsize,
    ) -> None:
        """Write the bytes from ``out_buffer`` to the device selected by ``address``, generate no stop
        bit, generate a repeated start and read into ``in_buffer``. ``out_buffer`` and
        ``in_buffer`` can be the same buffer because they are used sequentially.

        If ``out_start`` or ``out_end`` is provided, then the buffer will be sliced
        as if ``out_buffer[out_start:out_end]`` were passed, but without copying the data.
        The number of bytes written will be the length of ``out_buffer[start:end]``.

        If ``in_start`` or ``in_end`` is provided, then the input buffer will be sliced
        as if ``in_buffer[in_start:in_end]`` were passed,
        The number of bytes read will be the length of ``out_buffer[in_start:in_end]``.

        :param int address: 7-bit device address
        :param ~circuitpython_typing.ReadableBuffer out_buffer: buffer containing the bytes to write
        :param ~circuitpython_typing.WriteableBuffer in_buffer: buffer to write into
        :param int out_start: beginning of ``out_buffer`` slice
        :param int out_end: end of ``out_buffer`` slice; if not specified, use ``len(out_buffer)``
        :param int in_start: beginning of ``in_buffer`` slice
        :param int in_end: end of ``in_buffer slice``; if not specified, use ``len(in_buffer)``
        """
        ...

class SPI:
    """A 3-4 wire serial protocol

    SPI is a serial protocol that has exclusive pins for data in and out of the
    main device.  It is typically faster than :py:class:`~bitbangio.I2C` because a
    separate pin is used to select a device rather than a transmitted
    address. This class only manages three of the four SPI lines: `!clock`,
    `!MOSI`, `!MISO`. It is up to the client to manage the appropriate
    select line, often abbreviated `!CS` or `!SS`. (This is common because
    multiple secondaries can share the `!clock`, `!MOSI` and `!MISO` lines
    and therefore the hardware.)

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["busio.SPI"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    .. seealso:: This class acts as an SPI main (controller).
        To act as an SPI secondary (target), use `spitarget.SPITarget`.
    """

    def __init__(
        self,
        clock: microcontroller.Pin,
        MOSI: Optional[microcontroller.Pin] = None,
        MISO: Optional[microcontroller.Pin] = None,
        half_duplex: bool = False,
    ) -> None:
        """Construct an SPI object on the given pins.

        .. note:: The SPI peripherals allocated in order of desirability, if possible,
           such as highest speed and not shared use first. For instance, on the nRF52840,
           there is a single 32MHz SPI peripheral, and multiple 8MHz peripherals,
           some of which may also be used for I2C. The 32MHz SPI peripheral is returned
           first, then the exclusive 8MHz SPI peripheral, and finally the shared 8MHz
           peripherals.

        .. seealso:: Using this class directly requires careful lock management.
            Instead, use :class:`~adafruit_bus_device.SPIDevice` to
            manage locks.

        .. seealso:: Using this class to directly read registers requires manual
            bit unpacking. Instead, use an existing driver or make one with
            :ref:`Register <register-module-reference>` data descriptors.

        :param ~microcontroller.Pin clock: the pin to use for the clock.
        :param ~microcontroller.Pin MOSI: the Main Out Selected In pin.
        :param ~microcontroller.Pin MISO: the Main In Selected Out pin.
        :param bool half_duplex: True when MOSI is used for bidirectional data. False when SPI is full-duplex or simplex.

        **Limitations:** ``half_duplex`` is available only on STM; other chips do not have the hardware support.
        """
        ...

    def deinit(self) -> None:
        """Turn off the SPI bus."""
        ...

    def __enter__(self) -> SPI:
        """No-op used by Context Managers.
        Provided by context manager helper."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def configure(
        self,
        *,
        baudrate: int = 100000,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
    ) -> None:
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

    def try_lock(self) -> bool:
        """Attempts to grab the SPI lock. Returns True on success.

        :return: True when lock has been grabbed
        :rtype: bool"""
        ...

    def unlock(self) -> None:
        """Releases the SPI lock."""
        ...
    import sys

    def write(
        self, buffer: ReadableBuffer, *, start: int = 0, end: int = sys.maxsize
    ) -> None:
        """Write the data contained in ``buffer``. The SPI object must be locked.
        If the buffer is empty, nothing happens.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]`` were passed, but without copying the data.
        The number of bytes written will be the length of ``buffer[start:end]``.

        :param ReadableBuffer buffer: write out bytes from this buffer
        :param int start: beginning of buffer slice
        :param int end: end of buffer slice; if not specified, use ``len(buffer)``
        """
        ...
    import sys

    def readinto(
        self,
        buffer: WriteableBuffer,
        *,
        start: int = 0,
        end: int = sys.maxsize,
        write_value: int = 0,
    ) -> None:
        """Read into ``buffer`` while writing ``write_value`` for each byte read.
        The SPI object must be locked.
        If the number of bytes to read is 0, nothing happens.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]`` were passed.
        The number of bytes read will be the length of ``buffer[start:end]``.

        :param WriteableBuffer buffer: read bytes into this buffer
        :param int start: beginning of buffer slice
        :param int end: end of buffer slice; if not specified, it will be the equivalent value
            of ``len(buffer)`` and for any value provided it will take the value of
            ``min(end, len(buffer))``
        :param int write_value: value to write while reading
        """
        ...
    import sys

    def write_readinto(
        self,
        out_buffer: ReadableBuffer,
        in_buffer: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: int = sys.maxsize,
        in_start: int = 0,
        in_end: int = sys.maxsize,
    ) -> None:
        """Write out the data in ``out_buffer`` while simultaneously reading data into ``in_buffer``.
        The SPI object must be locked.

        If ``out_start`` or ``out_end`` is provided, then the buffer will be sliced
        as if ``out_buffer[out_start:out_end]`` were passed, but without copying the data.
        The number of bytes written will be the length of ``out_buffer[out_start:out_end]``.

        If ``in_start`` or ``in_end`` is provided, then the input buffer will be sliced
        as if ``in_buffer[in_start:in_end]`` were passed,
        The number of bytes read will be the length of ``out_buffer[in_start:in_end]``.

        The lengths of the slices defined by ``out_buffer[out_start:out_end]``
        and ``in_buffer[in_start:in_end]`` must be equal.
        If buffer slice lengths are both 0, nothing happens.

        :param ReadableBuffer out_buffer: write out bytes from this buffer
        :param WriteableBuffer in_buffer: read bytes into this buffer
        :param int out_start: beginning of ``out_buffer`` slice
        :param int out_end: end of ``out_buffer`` slice; if not specified, use ``len(out_buffer)``
        :param int in_start: beginning of ``in_buffer`` slice
        :param int in_end: end of ``in_buffer slice``; if not specified, use ``len(in_buffer)``
        """
        ...
    frequency: int
    """The actual SPI bus frequency. This may not match the frequency requested
    due to internal limitations."""

class UART:
    """A bidirectional serial protocol

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["busio.UART"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    """

    def __init__(
        self,
        tx: Optional[microcontroller.Pin] = None,
        rx: Optional[microcontroller.Pin] = None,
        *,
        rts: Optional[microcontroller.Pin] = None,
        cts: Optional[microcontroller.Pin] = None,
        rs485_dir: Optional[microcontroller.Pin] = None,
        rs485_invert: bool = False,
        baudrate: int = 9600,
        bits: int = 8,
        parity: Optional[Parity] = None,
        stop: int = 1,
        timeout: float = 1,
        receiver_buffer_size: int = 64,
    ) -> None:
        """A common bidirectional serial protocol that uses an an agreed upon speed
        rather than a shared clock line.

        :param ~microcontroller.Pin tx: the pin to transmit with, or ``None`` if this ``UART`` is receive-only.
        :param ~microcontroller.Pin rx: the pin to receive on, or ``None`` if this ``UART`` is transmit-only.
        :param ~microcontroller.Pin rts: the pin for rts, or ``None`` if rts not in use.
        :param ~microcontroller.Pin cts: the pin for cts, or ``None`` if cts not in use.
        :param ~microcontroller.Pin rs485_dir: the output pin for rs485 direction setting, or ``None`` if rs485 not in use.
        :param bool rs485_invert: rs485_dir pin active high when set. Active low otherwise.
        :param int baudrate: the transmit and receive speed.
        :param int bits:  the number of bits per byte, 5 to 9.
        :param Parity parity:  the parity used for error checking.
        :param int stop:  the number of stop bits, 1 or 2.
        :param float timeout:  the timeout in seconds to wait for the first character and between subsequent characters when reading. Raises ``ValueError`` if timeout >100 seconds.
        :param int receiver_buffer_size: the character length of the read buffer (0 to disable). (When a character is 9 bits the buffer will be 2 * receiver_buffer_size bytes.)

        ``tx`` and ``rx`` cannot both be ``None``.

        *New in CircuitPython 4.0:* ``timeout`` has incompatibly changed units from milliseconds to seconds.
        The new upper limit on ``timeout`` is meant to catch mistaken use of milliseconds.

        **Limitations:** RS485 is not supported on SAMD, Nordic, Broadcom, Spresense, or STM.
        On i.MX and Raspberry Pi RP2040, RS485 support is implemented in software:
        The timing for the ``rs485_dir`` pin signal is done on a best-effort basis, and may not meet
        RS485 specifications intermittently.
        """
        ...

    def deinit(self) -> None:
        """Deinitialises the UART and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> UART:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def read(self, nbytes: Optional[int] = None) -> Optional[bytes]:
        """Read bytes.  If ``nbytes`` is specified then read at most that many
        bytes. Otherwise, read everything that arrives until the connection
        times out. Providing the number of bytes expected is highly recommended
        because it will be faster. If no bytes are read, return ``None``.

        .. note:: When no bytes are read due to a timeout, this function returns ``None``.
          This matches the behavior of `io.RawIOBase.read` in Python 3, but
          differs from pyserial which returns ``b''`` in that situation.

        :return: Data read
        :rtype: bytes or None"""
        ...

    def readinto(self, buf: WriteableBuffer) -> Optional[int]:
        """Read bytes into the ``buf``. Read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)

        *New in CircuitPython 4.0:* No length parameter is permitted."""
        ...

    def readline(self) -> bytes:
        """Read a line, ending in a newline character, or
        return ``None`` if a timeout occurs sooner, or
        return everything readable if no newline is found and
        ``timeout=0``

        :return: the line read
        :rtype: bytes or None"""
        ...

    def write(self, buf: ReadableBuffer) -> Optional[int]:
        """Write the buffer of bytes to the bus.

        *New in CircuitPython 4.0:* ``buf`` must be bytes, not a string.

          :return: the number of bytes written
          :rtype: int or None"""
        ...
    baudrate: int
    """The current baudrate."""
    in_waiting: int
    """The number of bytes in the input buffer, available to be read"""
    timeout: float
    """The current timeout, in seconds (float)."""

    def reset_input_buffer(self) -> None:
        """Discard any unread characters in the input buffer."""
        ...

class Parity:
    """Enum-like class to define the parity used to verify correct data transfer."""

    ODD: int
    """Total number of ones should be odd."""

    EVEN: int
    """Total number of ones should be even."""
