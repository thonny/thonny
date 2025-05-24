"""Bluetooth Low Energy (BLE) communication

The `_bleio` module provides necessary low-level functionality for communicating
using Bluetooth Low Energy (BLE). The '_' prefix indicates this module is meant
for internal use by libraries but not by the end user. Its API may change incompatibly
between minor versions of CircuitPython.
Please use the
`adafruit_ble <https://circuitpython.readthedocs.io/projects/ble/en/latest/>`_
CircuitPython library instead, which builds on `_bleio`, and
provides higher-level convenience functionality, including predefined beacons, clients,
servers.

.. note:: `_bleio` uses native BLE capability on boards that support it, including Nordic nRF,
  Espressif (except ESP32-S2 and ESP32-P4), and SiLabs.
  On other boards, `_bleio`, if present, supports BLE using an AirLift co-processor.
  Pico W boards do *not* support BLE using the on-board CYW43 co-processor,
  but do support using an external AirLift.
"""

from __future__ import annotations

from typing import Iterable, Iterator, Optional, Tuple, Union

import _bleio
import busio
import digitalio
from circuitpython_typing import ReadableBuffer, WriteableBuffer

adapter: Adapter
"""BLE Adapter used to manage device discovery and connections.
This object is the sole instance of `_bleio.Adapter`."""

class BluetoothError(Exception):
    """Catchall exception for Bluetooth related errors."""

    ...

class RoleError(BluetoothError):
    """Raised when a resource is used as the mismatched role. For example, if a local CCCD is
    attempted to be set but they can only be set when remote."""

    ...

class SecurityError(BluetoothError):
    """Raised when a security related error occurs."""

    ...

def set_adapter(adapter: Optional[_bleio.Adapter]) -> None:
    """Set the adapter to use for BLE, such as when using an HCI adapter.
    Raises `NotImplementedError` when the adapter is a singleton and cannot be set."""
    ...

class Adapter:
    """
    The BLE Adapter object manages the discovery and connection to other nearby Bluetooth Low Energy devices.
    This part of the Bluetooth Low Energy Specification is known as Generic Access Profile (GAP).

    Discovery of other devices happens during a scanning process that listens for small packets of
    information, known as advertisements, that are broadcast unencrypted. The advertising packets
    have two different uses. The first is to broadcast a small piece of data to anyone who cares and
    and nothing more. These are known as beacons. The second class of advertisement is to promote
    additional functionality available after the devices establish a connection. For example, a
    BLE heart rate monitor would advertise that it provides the standard BLE Heart Rate Service.

    The Adapter can do both parts of this process: it can scan for other device
    advertisements and it can advertise its own data. Furthermore, Adapters can accept incoming
    connections and also initiate connections."""

    def __init__(
        self,
        *,
        uart: busio.UART,
        rts: digitalio.DigitalInOut,
        cts: digitalio.DigitalInOut,
    ) -> None:
        """On boards that do not have native BLE, you can use an HCI co-processor.
        Pass the uart and pins used to communicate with the co-processor, such as an Adafruit AirLift.
        The co-processor must have been reset and put into BLE mode beforehand
        by the appropriate pin manipulation.
        The ``uart``, ``rts``, and ``cts`` objects are used to
        communicate with the HCI co-processor in HCI mode.
        The `Adapter` object is enabled during this call.

        After instantiating an Adapter, call `_bleio.set_adapter()` to set `_bleio.adapter`

        On boards with native BLE, you cannot create an instance of `_bleio.Adapter`;
        this constructor will raise `NotImplementedError`.
        Use `_bleio.adapter` to access the sole instance already available.
        """
        ...
    enabled: bool
    """State of the BLE adapter."""
    address: Address
    """MAC address of the BLE adapter."""
    name: str
    """name of the BLE adapter used once connected.
    The name is "CIRCUITPY" + the last four hex digits of ``adapter.address``,
    to make it easy to distinguish multiple CircuitPython boards."""

    def start_advertising(
        self,
        data: ReadableBuffer,
        *,
        scan_response: Optional[ReadableBuffer] = None,
        connectable: bool = True,
        anonymous: bool = False,
        timeout: int = 0,
        interval: float = 0.1,
        tx_power: int = 0,
        directed_to: Optional[Address] = None,
    ) -> None:
        """Starts advertising until `stop_advertising` is called or if connectable, another device
        connects to us.

        .. warning:: If data is longer than 31 bytes, then this will automatically advertise as an
           extended advertisement that older BLE 4.x clients won't be able to scan for.

        .. note:: If you set ``anonymous=True``, then a timeout must be specified. If no timeout is
           specified, then the maximum allowed timeout will be selected automatically.

        :param ~circuitpython_typing.ReadableBuffer data: advertising data packet bytes
        :param ~circuitpython_typing.ReadableBuffer scan_response: scan response data packet bytes. ``None`` if no scan response is needed.
        :param bool connectable:  If `True` then other devices are allowed to connect to this peripheral.
        :param bool anonymous:  If `True` then this device's MAC address is randomized before advertising.
        :param int timeout:  If set, we will only advertise for this many seconds. Zero means no timeout.
        :param float interval:  advertising interval, in seconds
        :param int tx_power: transmitter power while advertising in dBm
        :param Address directed_to: peer to advertise directly to"""
        ...

    def stop_advertising(self) -> None:
        """Stop sending advertising packets."""
        ...

    def start_scan(
        self,
        prefixes: ReadableBuffer = b"",
        *,
        buffer_size: int = 512,
        extended: bool = False,
        timeout: Optional[float] = None,
        interval: float = 0.1,
        window: float = 0.1,
        minimum_rssi: int = -80,
        active: bool = True,
    ) -> Iterable[ScanEntry]:
        """Starts a BLE scan and returns an iterator of results. Advertisements and scan responses are
        filtered and returned separately.

        :param ~circuitpython_typing.ReadableBuffer prefixes: Sequence of byte string prefixes to filter advertising packets
            with. A packet without an advertising structure that matches one of the prefixes is
            ignored. Format is one byte for length (n) and n bytes of prefix and can be repeated.
        :param int buffer_size: the maximum number of advertising bytes to buffer.
        :param bool extended: When True, support extended advertising packets. Increasing buffer_size is recommended when this is set.
        :param float timeout: the scan timeout in seconds. If None or zero, will scan until `stop_scan` is called.
        :param float interval: the interval (in seconds) between the start of two consecutive scan windows
           Must be in the range 0.0025 - 40.959375 seconds.
        :param float window: the duration (in seconds) to scan a single BLE channel.
           window must be <= interval.
        :param int minimum_rssi: the minimum rssi of entries to return.
        :param bool active: retrieve scan responses for scannable advertisements.
        :returns: an iterable of `_bleio.ScanEntry` objects
        :rtype: iterable"""
        ...

    def stop_scan(self) -> None:
        """Stop the current scan."""
        ...
    advertising: bool
    """True when the adapter is currently advertising. (read-only)"""
    connected: bool
    """True when the adapter is connected to another device regardless of who initiated the
    connection. (read-only)"""
    connections: Tuple[Connection]
    """Tuple of active connections including those initiated through
    :py:meth:`_bleio.Adapter.connect`. (read-only)"""

    def connect(self, address: Address, *, timeout: float) -> Connection:
        """Attempts a connection to the device with the given address.

        :param Address address: The address of the peripheral to connect to
        :param float/int timeout: Try to connect for timeout seconds."""
        ...

    def erase_bonding(self) -> None:
        """Erase all bonding information stored in flash memory."""
        ...

class Address:
    """Encapsulates the address of a BLE device."""

    def __init__(self, address: ReadableBuffer, address_type: int) -> None:
        """Create a new Address object encapsulating the address value.
        The value itself can be one of:

        :param ~circuitpython_typing.ReadableBuffer address: The address value to encapsulate. A buffer object (bytearray, bytes) of 6 bytes.
        :param int address_type: one of the integer values: `PUBLIC`, `RANDOM_STATIC`,
          `RANDOM_PRIVATE_RESOLVABLE`, or `RANDOM_PRIVATE_NON_RESOLVABLE`."""
        ...
    address_bytes: bytes
    """The bytes that make up the device address (read-only).

    Note that the ``bytes`` object returned is in little-endian order:
    The least significant byte is ``address_bytes[0]``. So the address will
    appear to be reversed if you print the raw ``bytes`` object. If you print
    or use `str()` on the :py:class:`~_bleio.Attribute` object itself, the address will be printed
    in the expected order. For example:

    .. code-block:: python

      >>> import _bleio
      >>> _bleio.adapter.address
      <Address c8:1d:f5:ed:a8:35>
      >>> _bleio.adapter.address.address_bytes
      b'5\\xa8\\xed\\xf5\\x1d\\xc8'"""
    type: int
    """The address type (read-only).

    One of the integer values: `PUBLIC`, `RANDOM_STATIC`, `RANDOM_PRIVATE_RESOLVABLE`,
    or `RANDOM_PRIVATE_NON_RESOLVABLE`."""

    def __eq__(self, other: object) -> bool:
        """Two Address objects are equal if their addresses and address types are equal."""
        ...

    def __hash__(self) -> int:
        """Returns a hash for the Address data."""
        ...
    PUBLIC: int
    """A publicly known address, with a company ID (high 24 bits)and company-assigned part (low 24 bits)."""

    RANDOM_STATIC: int
    """A randomly generated address that does not change often. It may never change or may change after
     a power cycle."""

    RANDOM_PRIVATE_RESOLVABLE: int
    """An address that is usable when the peer knows the other device's secret Identity Resolving Key (IRK)."""

    RANDOM_PRIVATE_NON_RESOLVABLE: int
    """A randomly generated address that changes on every connection."""

class Attribute:
    """Definitions associated with all BLE attributes: characteristics, descriptors, etc.

    :py:class:`~_bleio.Attribute` is, notionally, a superclass of
    :py:class:`~Characteristic` and :py:class:`~Descriptor`,
    but is not defined as a Python superclass of those classes."""

    def __init__(self) -> None:
        """You cannot create an instance of :py:class:`~_bleio.Attribute`."""
        ...
    NO_ACCESS: int
    """security mode: access not allowed"""

    OPEN: int
    """security_mode: no security (link is not encrypted)"""

    ENCRYPT_NO_MITM: int
    """security_mode: unauthenticated encryption, without man-in-the-middle protection"""

    ENCRYPT_WITH_MITM: int
    """security_mode: authenticated encryption, with man-in-the-middle protection"""

    LESC_ENCRYPT_WITH_MITM: int
    """security_mode: LESC encryption, with man-in-the-middle protection"""

    SIGNED_NO_MITM: int
    """security_mode: unauthenticated data signing, without man-in-the-middle protection"""

    SIGNED_WITH_MITM: int
    """security_mode: authenticated data signing, without man-in-the-middle protection"""

class Characteristic:
    """Stores information about a BLE service characteristic and allows reading
    and writing of the characteristic's value."""

    def __init__(self) -> None:
        """There is no regular constructor for a Characteristic. A new local Characteristic can be created
        and attached to a Service by calling `add_to_service()`.
        Remote Characteristic objects are created by `Connection.discover_remote_services()`
        as part of remote Services."""
        ...

    @classmethod
    def add_to_service(
        cls,
        service: Service,
        uuid: UUID,
        *,
        properties: int = 0,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        max_length: int = 20,
        fixed_length: bool = False,
        initial_value: Optional[ReadableBuffer] = None,
        user_description: Optional[str] = None,
    ) -> Characteristic:
        """Create a new Characteristic object, and add it to this Service.

        :param Service service: The service that will provide this characteristic
        :param UUID uuid: The uuid of the characteristic
        :param int properties: The properties of the characteristic,
           specified as a bitmask of these values bitwise-or'd together:
           `BROADCAST`, `INDICATE`, `NOTIFY`, `READ`, `WRITE`, `WRITE_NO_RESPONSE`.
        :param int read_perm: Specifies whether the characteristic can be read by a client, and if so, which
           security mode is required. Must be one of the integer values `Attribute.NO_ACCESS`, `Attribute.OPEN`,
           `Attribute.ENCRYPT_NO_MITM`, `Attribute.ENCRYPT_WITH_MITM`, `Attribute.LESC_ENCRYPT_WITH_MITM`,
           `Attribute.SIGNED_NO_MITM`, or `Attribute.SIGNED_WITH_MITM`.
        :param int write_perm: Specifies whether the characteristic can be written by a client, and if so, which
           security mode is required. Values allowed are the same as ``read_perm``.
        :param int max_length: Maximum length in bytes of the characteristic value. The maximum allowed is
         is 512, or possibly 510 if ``fixed_length`` is False. The default, 20, is the maximum
         number of data bytes that fit in a single BLE 4.x ATT packet.
        :param bool fixed_length: True if the characteristic value is of fixed length.
        :param ~circuitpython_typing.ReadableBuffer initial_value: The initial value for this characteristic. If not given, will be
         filled with zeros.
        :param str user_description: User friendly description of the characteristic

        :return: the new Characteristic."""
        ...

    def deinit(self) -> None:
        """Deinitialises the Characteristic and releases any hardware resources for reuse."""
        ...
    properties: int
    """An int bitmask representing which properties are set, specified as bitwise or'ing of
    of these possible values.
    `BROADCAST`, `INDICATE`, `NOTIFY`, `READ`, `WRITE`, `WRITE_NO_RESPONSE`."""
    uuid: Optional[UUID]
    """The UUID of this characteristic. (read-only)

    Will be ``None`` if the 128-bit UUID for this characteristic is not known."""
    value: bytearray
    """The value of this characteristic."""
    max_length: int
    """The max length of this characteristic."""
    descriptors: Descriptor
    """A tuple of :py:class:`Descriptor` objects related to this characteristic. (read-only)"""
    service: Service
    """The Service this Characteristic is a part of."""

    def set_cccd(self, *, notify: bool = False, indicate: bool = False) -> None:
        """Set the remote characteristic's CCCD to enable or disable notification and indication.

        :param bool notify: True if Characteristic should receive notifications of remote writes
        :param float indicate: True if Characteristic should receive indications of remote writes
        """
        ...
    BROADCAST: int
    """property: allowed in advertising packets"""

    INDICATE: int
    """property: server will indicate to the client when the value is set and wait for a response"""

    NOTIFY: int
    """property: server will notify the client when the value is set"""

    READ: int
    """property: clients may read this characteristic"""

    WRITE: int
    """property: clients may write this characteristic; a response will be sent back"""

    WRITE_NO_RESPONSE: int
    """property: clients may write this characteristic; no response will be sent back"""

class CharacteristicBuffer:
    """Accumulates a Characteristic's incoming values in a FIFO buffer."""

    def __init__(
        self,
        characteristic: Characteristic,
        *,
        timeout: float = 1.0,
        buffer_size: int = 64,
    ) -> None:
        """Monitor the given Characteristic. Each time a new value is written to the Characteristic
        add the newly-written bytes to a FIFO buffer.

        :param Characteristic characteristic: The Characteristic to monitor.
          It may be a local Characteristic provided by a Peripheral Service, or a remote Characteristic
          in a remote Service that a Central has connected to.
        :param float timeout:  the timeout in seconds to wait for the first character and between subsequent characters.
        :param int buffer_size: Size of ring buffer that stores incoming data coming from client.
          Must be >= 1."""
        ...

    def read(self, nbytes: Optional[int] = None) -> Optional[bytes]:
        """Read characters.  If ``nbytes`` is specified then read at most that many
        bytes. Otherwise, read everything that arrives until the connection
        times out. Providing the number of bytes expected is highly recommended
        because it will be faster.

        :return: Data read
        :rtype: bytes or None"""
        ...

    def readinto(
        self, buf: WriteableBuffer, nbytes: Optional[int] = None
    ) -> Optional[int]:
        """Read bytes into the ``buf``. Read at most ``len(buf)`` bytes.

         You may reduce this maximum read using the ``nbytes`` argument.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)"""
        ...

    def readline(self) -> bytes:
        """Read a line, ending in a newline character.

        :return: the line read
        :rtype: int or None"""
        ...
    in_waiting: int
    """The number of bytes in the input buffer, available to be read"""

    def reset_input_buffer(self) -> None:
        """Discard any unread characters in the input buffer."""
        ...

    def deinit(self) -> None:
        """Disable permanently."""
        ...

class Connection:
    """A BLE connection to another device. Used to discover and interact with services on the other
    device.

    Usage::

       import _bleio

       my_entry = None
       for entry in _bleio.adapter.scan(2.5):
           if entry.name is not None and entry.name == 'InterestingPeripheral':
               my_entry = entry
               break

       if not my_entry:
           raise Exception("'InterestingPeripheral' not found")

       connection = _bleio.adapter.connect(my_entry.address, timeout=10)"""

    def __init__(self) -> None:
        """Connections cannot be made directly. Instead, to initiate a connection use `Adapter.connect`.
        Connections may also be made when another device initiates a connection. To use a Connection
        created by a peer, read the `Adapter.connections` property."""
        ...

    def disconnect(self) -> None:
        """Disconnects from the remote peripheral. Does nothing if already disconnected."""
        ...

    def pair(self, *, bond: bool = True) -> None:
        """Pair to the peer to improve security.

        **Limitation**: Currently ``bond``must be ``True``: bonding always occurs.
        """
        ...

    def discover_remote_services(
        self, service_uuids_whitelist: Optional[Iterable[UUID]] = None
    ) -> Tuple[Service, ...]:
        """Do BLE discovery for all services or for the given service UUIDS,
        to find their handles and characteristics, and return the discovered services.
        `Connection.connected` must be True.

        :param iterable service_uuids_whitelist:

          an iterable of :py:class:`UUID` objects for the services provided by the peripheral
          that you want to use.

          The peripheral may provide more services, but services not listed are ignored
          and will not be returned.

          If service_uuids_whitelist is None, then all services will undergo discovery, which can be
          slow.

          If the service UUID is 128-bit, or its characteristic UUID's are 128-bit, you
          you must have already created a :py:class:`UUID` object for that UUID in order for the
          service or characteristic to be discovered. Creating the UUID causes the UUID to be
          registered for use. (This restriction may be lifted in the future.)

        :return: A tuple of `_bleio.Service` objects provided by the remote peripheral.
        """
        ...
    connected: bool
    """True if connected to the remote peer."""
    paired: bool
    """True if paired to the remote peer."""
    connection_interval: float
    """Time between transmissions in milliseconds. Will be multiple of 1.25ms. Lower numbers
    increase speed and decrease latency but increase power consumption.

    When setting connection_interval, the peer may reject the new interval and
    `connection_interval` will then remain the same.

    Apple has additional guidelines that dictate should be a multiple of 15ms except if HID is
    available. When HID is available Apple devices may accept 11.25ms intervals."""
    max_packet_length: int
    """The maximum number of data bytes that can be sent in a single transmission,
    not including overhead bytes.

    This is the maximum number of bytes that can be sent in a notification,
    which must be sent in a single packet.
    But for a regular characteristic read or write, may be sent in multiple packets,
    so this limit does not apply."""

class Descriptor:
    """Stores information about a BLE descriptor.

    Descriptors are attached to BLE characteristics and provide contextual
    information about the characteristic."""

    def __init__(self) -> None:
        """There is no regular constructor for a Descriptor. A new local Descriptor can be created
        and attached to a Characteristic by calling `add_to_characteristic()`.
        Remote Descriptor objects are created by `Connection.discover_remote_services()`
        as part of remote Characteristics in the remote Services that are discovered."""

    @classmethod
    def add_to_characteristic(
        cls,
        characteristic: Characteristic,
        uuid: UUID,
        *,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        max_length: int = 20,
        fixed_length: bool = False,
        initial_value: ReadableBuffer = b"",
    ) -> Descriptor:
        """Create a new Descriptor object, and add it to this Service.

        :param Characteristic characteristic: The characteristic that will hold this descriptor
        :param UUID uuid: The uuid of the descriptor
        :param int read_perm: Specifies whether the descriptor can be read by a client, and if so, which
           security mode is required. Must be one of the integer values `Attribute.NO_ACCESS`, `Attribute.OPEN`,
           `Attribute.ENCRYPT_NO_MITM`, `Attribute.ENCRYPT_WITH_MITM`, `Attribute.LESC_ENCRYPT_WITH_MITM`,
           `Attribute.SIGNED_NO_MITM`, or `Attribute.SIGNED_WITH_MITM`.
        :param int write_perm: Specifies whether the descriptor can be written by a client, and if so, which
           security mode is required. Values allowed are the same as ``read_perm``.
        :param int max_length: Maximum length in bytes of the descriptor value. The maximum allowed is
           is 512, or possibly 510 if ``fixed_length`` is False. The default, 20, is the maximum
           number of data bytes that fit in a single BLE 4.x ATT packet.
        :param bool fixed_length: True if the descriptor value is of fixed length.
        :param ~circuitpython_typing.ReadableBuffer initial_value: The initial value for this descriptor.

        :return: the new Descriptor."""
        ...
    uuid: UUID
    """The descriptor uuid. (read-only)"""
    characteristic: Characteristic
    """The Characteristic this Descriptor is a part of."""
    value: bytearray
    """The value of this descriptor."""

class PacketBuffer:
    def __init__(
        self,
        characteristic: Characteristic,
        *,
        buffer_size: int,
        max_packet_size: Optional[int] = None,
    ) -> None:
        """Accumulates a Characteristic's incoming packets in a FIFO buffer and facilitates packet aware
        outgoing writes. A packet's size is either the characteristic length or the maximum transmission
        unit (MTU) minus overhead, whichever is smaller. The MTU can change so check `incoming_packet_length`
        and `outgoing_packet_length` before creating a buffer to store data.

        When we're the server, we ignore all connections besides the first to subscribe to
        notifications.

        :param Characteristic characteristic: The Characteristic to monitor.
          It may be a local Characteristic provided by a Peripheral Service, or a remote Characteristic
          in a remote Service that a Central has connected to.
        :param int buffer_size: Size of ring buffer (in packets of the Characteristic's maximum
          length) that stores incoming packets coming from the peer.
        :param int max_packet_size: Maximum size of packets. Overrides value from the characteristic.
          (Remote characteristics may not have the correct length.)"""
        ...

    def readinto(self, buf: WriteableBuffer) -> int:
        """Reads a single BLE packet into the ``buf``. Raises an exception if the next packet is longer
        than the given buffer. Use `incoming_packet_length` to read the maximum length of a single packet.

        :return: number of bytes read and stored into ``buf``
        :rtype: int"""
        ...

    def write(self, data: ReadableBuffer, *, header: Optional[bytes] = None) -> int:
        """Writes all bytes from data into the same outgoing packet. The bytes from header are included
        before data when the pending packet is currently empty.

        This does not block until the data is sent. It only blocks until the data is pending.

        :return: number of bytes written. May include header bytes when packet is empty.
        :rtype: int"""
        ...

    def deinit(self) -> None:
        """Disable permanently."""
        ...
    incoming_packet_length: int
    """Maximum length in bytes of a packet we are reading."""
    outgoing_packet_length: int
    """Maximum length in bytes of a packet we are writing."""

class ScanEntry:
    """Encapsulates information about a device that was received during scanning. It can be
    advertisement or scan response data. This object may only be created by a `_bleio.ScanResults`:
    it has no user-visible constructor."""

    def __init__(self) -> None:
        """Cannot be instantiated directly. Use `_bleio.Adapter.start_scan`."""
        ...

    def matches(self, prefixes: ReadableBuffer, *, match_all: bool = True) -> bool:
        """Returns True if the ScanEntry matches all prefixes when ``match_all`` is True. This is stricter
        than the scan filtering which accepts any advertisements that match any of the prefixes
        where ``match_all`` is False."""
        ...
    address: Address
    """The address of the device (read-only), of type `_bleio.Address`."""
    advertisement_bytes: bytes
    """All the advertisement data present in the packet, returned as a ``bytes`` object. (read-only)"""
    rssi: int
    """The signal strength of the device at the time of the scan, in integer dBm. (read-only)"""
    connectable: bool
    """True if the device can be connected to. (read-only)"""
    scan_response: bool
    """True if the entry was a scan response. (read-only)"""

class ScanResults:
    """Iterates over advertising data received while scanning. This object is always created
    by a `_bleio.Adapter`: it has no user-visible constructor."""

    def __init__(self) -> None:
        """Cannot be instantiated directly. Use `_bleio.Adapter.start_scan`."""
        ...

    def __iter__(self) -> Iterator[ScanEntry]:
        """Returns itself since it is the iterator."""
        ...

    def __next__(self) -> ScanEntry:
        """Returns the next `_bleio.ScanEntry`. Blocks if none have been received and scanning is still
        active. Raises `StopIteration` if scanning is finished and no other results are available.
        """
        ...

class Service:
    """Stores information about a BLE service and its characteristics."""

    def __init__(self, uuid: UUID, *, secondary: bool = False) -> None:
        """Create a new Service identified by the specified UUID. It can be accessed by all
        connections. This is known as a Service server. Client Service objects are created via
        `Connection.discover_remote_services`.

        To mark the Service as secondary, pass `True` as :py:data:`secondary`.

        :param UUID uuid: The uuid of the service
        :param bool secondary: If the service is a secondary one

        :return: the new Service"""
        ...

    def deinit(self) -> None:
        """Disable and deinitialise the Service."""
        ...
    characteristics: Tuple[Characteristic, ...]
    """A tuple of :py:class:`Characteristic` designating the characteristics that are offered by
    this service. (read-only)"""
    remote: bool
    """True if this is a service provided by a remote device. (read-only)"""
    secondary: bool
    """True if this is a secondary service. (read-only)"""
    uuid: Optional[UUID]
    """The UUID of this service. (read-only)

    Will be ``None`` if the 128-bit UUID for this service is not known."""

class UUID:
    """A 16-bit or 128-bit UUID. Can be used for services, characteristics, descriptors and more."""

    def __init__(self, value: Union[int, ReadableBuffer, str]) -> None:
        """Create a new UUID or UUID object encapsulating the uuid value.
        The value can be one of:

        - an `int` value in range 0 to 0xFFFF (Bluetooth SIG 16-bit UUID)
        - a buffer object (bytearray, bytes) of 16 bytes in little-endian order (128-bit UUID)
        - a string of hex digits of the form 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

        Creating a 128-bit UUID registers the UUID with the onboard BLE software, and provides a
        temporary 16-bit UUID that can be used in place of the full 128-bit UUID.

        :param value: The uuid value to encapsulate
        :type value: int, ~circuitpython_typing.ReadableBuffer or str"""
        ...
    uuid16: int
    """The 16-bit part of the UUID. (read-only)

    :type: int"""
    uuid128: bytes
    """The 128-bit value of the UUID
    Raises AttributeError if this is a 16-bit UUID. (read-only)

    :type: bytes"""
    size: int
    """128 if this UUID represents a 128-bit vendor-specific UUID. 16 if this UUID represents a
    16-bit Bluetooth SIG assigned UUID. (read-only) 32-bit UUIDs are not currently supported.

    :type: int"""

    def pack_into(self, buffer: WriteableBuffer, offset: int = 0) -> None:
        """Packs the UUID into the given buffer at the given offset."""
        ...

    def __eq__(self, other: object) -> bool:
        """Two UUID objects are equal if their values match and they are both 128-bit or both 16-bit."""
        ...
