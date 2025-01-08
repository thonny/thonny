"""CAN bus access

The `canio` module contains low level classes to support the CAN bus
protocol on microcontrollers that have built-in CAN peripherals.

Boards like the Adafruit RP2040 CAN Bus Feather that use an MCP2515 or
compatible chip use the `mcp2515:adafruit_mcp2515` module instead.

CAN and Listener classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import canio
  from board import *

  can = canio.CAN(board.CAN_RX, board.CAN_TX, baudrate=1000000)
  message = canio.Message(id=0x0408, data=b"adafruit")
  can.send(message)
  can.deinit()

This example will write the data 'adafruit' onto the CAN bus to any
device listening for message id 0x0408.

A CAN bus involves a transceiver, which is often a separate chip with a "standby" pin.
If your board has a CAN_STANDBY pin, ensure to set it to an output with the value False
to enable the transceiver.

Other implementations of the CAN device may exist (for instance, attached
via an SPI bus).  If so their constructor arguments may differ, but
otherwise we encourage implementors to follow the API that the core uses.

For more information on working with this module, refer to
`this Learn Guide on using it <https://learn.adafruit.com/using-canio-circuitpython>`_.
"""

from __future__ import annotations

from types import TracebackType
from typing import Optional, Sequence, Type, Union

import microcontroller

class BusState:
    """The state of the CAN bus"""

    ERROR_ACTIVE: object
    """The bus is in the normal (active) state"""

    ERROR_WARNING: object
    """The bus is in the normal (active) state, but a moderate number of errors have occurred recently.

    .. note:: Not all implementations may use ``ERROR_WARNING``.  Do not rely on seeing ``ERROR_WARNING`` before ``ERROR_PASSIVE``."""

    ERROR_PASSIVE: object
    """The bus is in the passive state due to the number of errors that have occurred recently.

    This device will acknowledge packets it receives, but cannot transmit messages.
    If additional errors occur, this device may progress to BUS_OFF.
    If it successfully acknowledges other packets on the bus, it can return to ERROR_WARNING or ERROR_ACTIVE and transmit packets.
    """

    BUS_OFF: object
    """The bus has turned off due to the number of errors that have
    occurred recently.  It must be restarted before it will send or receive
    packets.  This device will neither send or acknowledge packets on the bus."""

class CAN:
    """CAN bus protocol"""

    def __init__(
        self,
        tx: microcontroller.Pin,
        rx: microcontroller.Pin,
        *,
        baudrate: int = 250000,
        loopback: bool = False,
        silent: bool = False,
        auto_restart: bool = False,
    ) -> None:
        """A common shared-bus protocol.  The rx and tx pins are generally
        connected to a transceiver which controls the H and L pins on a
        shared bus.

        :param ~microcontroller.Pin rx: the pin to receive with
        :param ~microcontroller.Pin tx: the pin to transmit with
        :param int baudrate: The bit rate of the bus in Hz.  All devices on the bus must agree on this value.
        :param bool loopback: When True  the ``rx`` pin's value is ignored, and the device receives the packets it sends.
        :param bool silent: When True the ``tx`` pin is always driven to the high logic level.  This mode can be used to "sniff" a CAN bus without interfering.
        :param bool auto_restart: If True, will restart communications after entering bus-off state
        """
        ...
    auto_restart: bool
    """If True, will restart communications after entering bus-off state"""
    baudrate: int
    """The baud rate (read-only)"""
    transmit_error_count: int
    """The number of transmit errors (read-only).  Increased for a detected transmission error, decreased for successful transmission.  Limited to the range from 0 to 255 inclusive.  Also called TEC."""
    receive_error_count: int
    """The number of receive errors (read-only).  Increased for a detected reception error, decreased for successful reception.  Limited to the range from 0 to 255 inclusive.  Also called REC."""
    state: BusState
    """The current state of the bus. (read-only)"""
    def restart(self) -> None:
        """If the device is in the bus off state, restart it."""
        ...

    def listen(
        self, matches: Optional[Sequence[Match]] = None, *, timeout: float = 10
    ) -> Listener:
        """Start receiving messages that match any one of the filters.

        Creating a listener is an expensive operation and can interfere with reception of messages by other listeners.

        There is an implementation-defined maximum number of listeners and limit to the complexity of the filters.

        If the hardware cannot support all the requested matches, a ValueError is raised.  Note that generally there are some number of hardware filters shared among all fifos.

        A message can be received by at most one Listener.  If more than one listener matches a message, it is undefined which one actually receives it.

        An empty filter list causes all messages to be accepted.

        Timeout dictates how long receive() and next() will block.

        Platform specific notes:

        SAM E5x supports two Listeners.  Filter blocks are shared between the two
        listeners.  There are 4 standard filter blocks and 4 extended filter blocks.
        Each block can either match 2 single addresses or a mask of addresses.
        The number of filter blocks can be increased, up to a hardware maximum, by
        rebuilding CircuitPython, but this decreases the CircuitPython free
        memory even if canio is not used.

        STM32F405 supports two Listeners.  Filter blocks are shared between the two listeners.
        There are 14 filter blocks.  Each block can match 2 standard addresses with
        mask or 1 extended address with mask.

        ESP32S2 supports one Listener.  There is a single filter block, which can either match a
        standard address with mask or an extended address with mask.
        """
        ...
    loopback: bool
    """True if the device was created in loopback mode, False
    otherwise (read-only)"""
    def send(self, message: Union[RemoteTransmissionRequest, Message]) -> None:
        """Send a message on the bus with the given data and id.
        If the message could not be sent due to a full fifo or a bus error condition, RuntimeError is raised.
        """
        ...
    silent: bool
    """True if the device was created in silent mode, False
    otherwise (read-only)"""
    def deinit(self) -> None:
        """Deinitialize this object, freeing its hardware resources"""
        ...

    def __enter__(self) -> CAN:
        """Returns self, to allow the object to be used in a `with` statement for resource control"""
        ...

    def __exit__(
        self,
        unused1: Optional[Type[BaseException]],
        unused2: Optional[BaseException],
        unused3: Optional[TracebackType],
    ) -> None:
        """Calls deinit()"""
        ...

class Listener:
    """Listens for CAN message

    `canio.Listener` is not constructed directly, but instead by calling
    `canio.CAN.listen`.

    In addition to using the `receive` method to retrieve a message or
    the `in_waiting` method to check for an available message, a
    listener can be used as an iterable, yielding messages until no
    message arrives within ``self.timeout`` seconds."""

    def receive(self) -> Optional[Union[RemoteTransmissionRequest, Message]]:
        """Reads a message, after waiting up to ``self.timeout`` seconds

        If no message is received in time, `None` is returned.  Otherwise,
        a `Message` or `RemoteTransmissionRequest` is returned."""
        ...

    def in_waiting(self) -> int:
        """Returns the number of messages (including remote
        transmission requests) waiting"""
        ...

    def __iter__(self) -> Listener:
        """Returns self

        This method exists so that `Listener` can be used as an
        iterable"""
        ...

    def __next__(self) -> Union[RemoteTransmissionRequest, Message]:
        """Reads a message, after waiting up to self.timeout seconds

        If no message is received in time, raises StopIteration.  Otherwise,
        a Message or  is returned.

        This method enables the `Listener` to be used as an
        iterable, for instance in a for-loop."""
        ...

    def deinit(self) -> None:
        """Deinitialize this object, freeing its hardware resources"""
        ...

    def __enter__(self) -> CAN:
        """Returns self, to allow the object to be used in a `with` statement for resource control"""
        ...

    def __exit__(
        self,
        unused1: Optional[Type[BaseException]],
        unused2: Optional[BaseException],
        unused3: Optional[TracebackType],
    ) -> None:
        """Calls deinit()"""
        ...
    timeout: float

class Match:
    """Describe CAN bus messages to match"""

    def __init__(
        self, id: int, *, mask: Optional[int] = None, extended: bool = False
    ) -> None:
        """Construct a Match with the given properties.

        If mask is not None, then the filter is for any id which matches all
        the nonzero bits in mask. Otherwise, it matches exactly the given id.
        If extended is true then only extended ids are matched, otherwise
        only standard ids are matched."""
    id: int
    """The id to match"""
    mask: int
    """The optional mask of ids to match"""
    extended: bool
    """True to match extended ids, False to match standard ides"""

class Message:
    def __init__(self, id: int, data: bytes, *, extended: bool = False) -> None:
        """Construct a Message to send on a CAN bus.

        :param int id: The numeric ID of the message
        :param bytes data: The content of the message
        :param bool extended: True if the message has an extended identifier, False if it has a standard identifier

        In CAN, messages can have a length from 0 to 8 bytes.
        """
        ...
    id: int
    """The numeric ID of the message"""
    data: bytes
    """The content of the message"""
    extended: bool
    """True if the message's id is an extended id"""

class RemoteTransmissionRequest:
    def __init__(self, id: int, length: int, *, extended: bool = False) -> None:
        """Construct a RemoteTransmissionRequest to send on a CAN bus.

        :param int id: The numeric ID of the requested message
        :param int length: The length of the requested message
        :param bool extended: True if the message has an extended identifier, False if it has a standard identifier

        In CAN, messages can have a length from 0 to 8 bytes.
        """
        ...
    id: int
    """The numeric ID of the message"""
    extended: bool
    """True if the message's id is an extended id"""
    length: int
    """The length of the requested message."""
