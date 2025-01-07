"""Communicate with a device using a serial interface.
"""

from _typeshed import WriteableBuffer
from ..microbit import MicroBitDigitalPin
from typing import Optional, Union

ODD: int
"""Odd parity"""

EVEN: int
"""Even parity"""

def init(
    baudrate: int = 9600,
    bits: int = 8,
    parity: Optional[int] = None,
    stop: int = 1,
    tx: Optional[MicroBitDigitalPin] = None,
    rx: Optional[MicroBitDigitalPin] = None,
) -> None:
    """Initialize serial communication.

    Example: ``uart.init(115200, tx=pin0, rx=pin1)``

    :param baudrate: The speed of communication.
    :param bits: The size of bytes being transmitted. micro:bit only supports 8.
    :param parity: How parity is checked, ``None``, ``uart.ODD`` or ``uart.EVEN``.
    :param stop: The number of stop bits, has to be 1 for micro:bit.
    :param tx: Transmitting pin.
    :param rx: Receiving pin.

    Initializing the UART on external pins will cause the Python console on
    USB to become unaccessible, as it uses the same hardware. To bring the
    console back you must reinitialize the UART without passing anything for
    ``tx`` or ``rx`` (or passing ``None`` to these arguments).  This means
    that calling ``uart.init(115200)`` is enough to restore the Python console.

    For more details see `the online documentation <https://microbit-micropython.readthedocs.io/en/v2-docs/uart.html>`_.
    """
    ...

def any() -> bool:
    """Check if any data is waiting.

    Example: ``uart.any()``

    :return: ``True`` if any data is waiting, else ``False``.
    """
    ...

def read(nbytes: Optional[int] = None) -> Optional[bytes]:
    """Read bytes.

    Example: ``uart.read()``

    :param nbytes: If ``nbytes`` is specified then read at most that many bytes, otherwise read as many bytes as possible
    :return: A bytes object or ``None`` on timeout
    """
    ...

def readinto(buf: WriteableBuffer, nbytes: Optional[int] = None) -> Optional[int]:
    """Read bytes into the ``buf``.

    Example: ``uart.readinto(input_buffer)``

    :param buf: The buffer to write to.
    :param nbytes: If ``nbytes`` is specified then read at most that many bytes, otherwise read ``len(buf)`` bytes.
    :return: number of bytes read and stored into ``buf`` or ``None`` on timeout.
    """
    ...

def readline() -> Optional[bytes]:
    """Read a line, ending in a newline character.

    Example: ``uart.readline()``

    :return: The line read or ``None`` on timeout. The newline character is included in the returned bytes.
    """
    ...

def write(buf: Union[bytes, str]) -> Optional[int]:
    """Write a buffer to the bus.

    Example: ``uart.write('hello world')``

    :param buf: A bytes object or a string.
    :return: The number of bytes written, or ``None`` on timeout.

    Examples::

        uart.write('hello world')
        uart.write(b'hello world')
        uart.write(bytes([1, 2, 3]))
    """
    ...
