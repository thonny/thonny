"""ESP-NOW Module

The `espnow` module provides an interface to the
`ESP-NOW <https://docs.espressif.com/projects/esp-idf/en/release-v4.4/esp32/api-reference/network/esp_now.html>`_
protocol provided by Espressif on its SoCs.

**Sender**

.. code-block:: python

    import espnow

    e = espnow.ESPNow()
    peer = espnow.Peer(mac=b'\xaa\xaa\xaa\xaa\xaa\xaa')
    e.peers.append(peer)

    e.send("Starting...")
    for i in range(10):
        e.send(str(i)*20)
    e.send(b'end')

**Receiver**

.. code-block:: python

    import espnow

    e = espnow.ESPNow()
    packets = []

    while True:
        if e:
            packet = e.read()
            packets.append(packet)
            if packet.msg == b'end':
                break

    print("packets:", f"length={len(packets)}")
    for packet in packets:
        print(packet)
"""

from __future__ import annotations

from typing import Optional

from circuitpython_typing import ReadableBuffer

...

class ESPNow:
    """Provides access to the ESP-NOW protocol."""

    def __init__(self, buffer_size: int = 526, phy_rate: int = 0) -> None:
        """Allocate and initialize `ESPNow` instance as a singleton.

        :param int buffer_size: The size of the internal ring buffer. Default: 526 bytes.
        :param int phy_rate: The ESP-NOW physical layer rate. Default: 1 Mbps.
            `wifi_phy_rate_t <https://docs.espressif.com/projects/esp-idf/en/release-v4.4/esp32/api-reference/network/esp_wifi.html#_CPPv415wifi_phy_rate_t>`_
        """
        ...

    def deinit(self) -> None:
        """Deinitializes ESP-NOW and releases it for another program."""
        ...

    def __enter__(self) -> ESPNow:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def send(
        self,
        message: ReadableBuffer,
        peer: Optional[Peer] = None,
    ) -> None:
        """Send a message to the peer's mac address.

        This blocks until a timeout of ``2`` seconds if the ESP-NOW internal buffers are full.

        :param ReadableBuffer message: The message to send (length <= 250 bytes).
        :param Peer peer: Send message to this peer. If `None`, send to all registered peers.
        """
        ...

    def read(self) -> Optional[ESPNowPacket]:
        """Read a packet from the receive buffer.

        This is non-blocking, the packet is received asynchronously from the peer(s).

        :returns: An `ESPNowPacket` if available in the buffer, otherwise `None`."""
        ...
    send_success: int
    """The number of tx packets received by the peer(s) ``ESP_NOW_SEND_SUCCESS``. (read-only)"""

    send_failure: int
    """The number of failed tx packets ``ESP_NOW_SEND_FAIL``. (read-only)"""

    read_success: int
    """The number of rx packets captured in the buffer. (read-only)"""

    read_failure: int
    """The number of dropped rx packets due to buffer overflow. (read-only)"""

    def set_pmk(self, pmk: ReadableBuffer) -> None:
        """Set the ESP-NOW Primary Master Key (pmk) for encrypted communications.

        :param ReadableBuffer pmk: The ESP-NOW Primary Master Key (length = 16 bytes).
        """
        ...
    buffer_size: int
    """The size of the internal ring buffer. (read-only)"""

    phy_rate: int
    """The ESP-NOW physical layer rate.
    `wifi_phy_rate_t <https://docs.espressif.com/projects/esp-idf/en/release-v4.4/esp32/api-reference/network/esp_wifi.html#_CPPv415wifi_phy_rate_t>`_
    """

    peers: Peers
    """The peer info records for all registered `ESPNow` peers. (read-only)"""

    def __bool__(self) -> bool:
        """``True`` if `len()` is greater than zero.
        This is an easy way to check if the buffer is empty.
        """
        ...

    def __len__(self) -> int:
        """Return the number of `bytes` available to read. Used to implement ``len()``."""
        ...

class ESPNowPacket:
    """A packet retrieved from ESP-NOW communication protocol. A namedtuple."""

    mac: ReadableBuffer
    """The sender's mac address (length = 6 bytes)."""

    msg: ReadableBuffer
    """The message sent by the peer (length <= 250 bytes)."""

    rssi: int
    """The received signal strength indication (in dBm from -127 to 0)."""

    time: int
    """The time in milliseconds since the device last booted when the packet was received."""

class Peer:
    """A data class to store parameters specific to a peer."""

    def __init__(
        self,
        mac: bytes,
        *,
        lmk: Optional[bytes],
        channel: int = 0,
        interface: int = 0,
        encrypted: bool = False,
    ) -> None:
        """Construct a new peer object.

        :param bytes mac: The mac address of the peer.
        :param bytes lmk: The Local Master Key (lmk) of the peer.
        :param int channel: The peer's channel. Default: 0 ie. use the current channel.
        :param int interface: The WiFi interface to use. Default: 0 ie. STA.
        :param bool encrypted: Whether or not to use encryption.
        """
        ...
    mac: ReadableBuffer
    """The WiFi mac to use."""

    lmk: ReadableBuffer
    """The WiFi lmk to use."""

    channel: int
    """The WiFi channel to use."""

    interface: int
    """The WiFi interface to use."""

    encrypted: bool
    """Whether or not to use encryption."""

class Peers:
    """Maintains a `list` of `Peer` internally and only exposes a subset of `list` methods."""

    def __init__(self) -> None:
        """You cannot create an instance of `Peers`."""
        ...

    def append(self, peer: Peer) -> None:
        """Append peer.

        :param Peer peer: The peer object to append.
        """
        ...

    def remove(self, peer: Peer) -> None:
        """Remove peer.

        :param Peer peer: The peer object to remove.
        """
        ...
