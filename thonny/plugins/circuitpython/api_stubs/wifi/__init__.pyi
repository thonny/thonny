"""
The `wifi` module provides necessary low-level functionality for managing
wifi connections. Use `socketpool` for communicating over the network."""

from __future__ import annotations

import ipaddress
from typing import Iterable, Iterator, Optional, Union

from circuitpython_typing import ReadableBuffer

radio: Radio
"""Wifi radio used to manage both station and AP modes.
This object is the sole instance of `wifi.Radio`."""

class AuthMode:
    """The authentication protocols used by WiFi."""

    OPEN: object
    """Open network. No authentication required."""

    WEP: object
    """Wired Equivalent Privacy."""

    WPA: object
    """Wireless Protected Access."""

    WPA2: object
    """Wireless Protected Access 2."""

    WPA3: object
    """Wireless Protected Access 3."""

    PSK: object
    """Pre-shared Key. (password)"""

    ENTERPRISE: object
    """Each user has a unique credential."""

class Monitor:
    """For monitoring WiFi packets."""

def __init__(self, channel: Optional[int] = 1, queue: Optional[int] = 128) -> None:
    """Initialize `wifi.Monitor` singleton.

    :param int channel: The WiFi channel to scan.
    :param int queue: The queue size for buffering the packet.

    """
    ...

channel: int
"""The WiFi channel to scan."""

queue: int
"""The queue size for buffering the packet."""

def deinit(self) -> None:
    """De-initialize `wifi.Monitor` singleton."""
    ...

def lost(self) -> int:
    """Returns the packet loss count. The counter resets after each poll."""
    ...

def queued(self) -> int:
    """Returns the packet queued count."""
    ...

def packet(self) -> dict:
    """Returns the monitor packet."""
    ...

class Network:
    """A wifi network provided by a nearby access point."""

    def __init__(self) -> None:
        """You cannot create an instance of `wifi.Network`. They are returned by `wifi.Radio.start_scanning_networks`."""
        ...
    ssid: str
    """String id of the network"""

    bssid: bytes
    """BSSID of the network (usually the AP's MAC address)"""

    rssi: int
    """Signal strength of the network"""

    channel: int
    """Channel number the network is operating on"""

    country: str
    """String id of the country code"""

    authmode: str
    """String id of the authmode"""

class Packet:
    """The packet parameters."""

    CH: object
    """The packet's channel."""

    LEN: object
    """The packet's length."""

    RAW: object
    """The packet's payload."""

    RSSI: object
    """The packet's rssi."""

class Radio:
    """Native wifi radio.

    This class manages the station and access point functionality of the native
    Wifi radio.

    """

    def __init__(self) -> None:
        """You cannot create an instance of `wifi.Radio`.
        Use `wifi.radio` to access the sole instance available."""
        ...
    enabled: bool
    """``True`` when the wifi radio is enabled.
    If you set the value to ``False``, any open sockets will be closed.
    """

    hostname: Union[str | ReadableBuffer]
    """Hostname for wifi interface. When the hostname is altered after interface started/connected
       the changes would only be reflected once the interface restarts/reconnects."""

    mac_address: ReadableBuffer
    """MAC address for the station. When the address is altered after interface is connected
       the changes would only be reflected once the interface reconnects."""

    mac_address_ap: ReadableBuffer
    """MAC address for the AP. When the address is altered after interface is started
       the changes would only be reflected once the interface restarts."""

    def start_scanning_networks(
        self, *, start_channel: int = 1, stop_channel: int = 11
    ) -> Iterable[Network]:
        """Scans for available wifi networks over the given channel range. Make sure the channels are allowed in your country."""
        ...
    def stop_scanning_networks(self) -> None:
        """Stop scanning for Wifi networks and free any resources used to do it."""
        ...
    def start_station(self) -> None:
        """Starts a Station."""
        ...
    def stop_station(self) -> None:
        """Stops the Station."""
        ...
    def start_ap(
        self,
        ssid: Union[str | ReadableBuffer],
        password: Union[str | ReadableBuffer] = "",
        *,
        channel: Optional[int] = 1,
        authmode: Optional[AuthMode],
        max_connections: Optional[int] = 4,
    ) -> None:
        """Starts an Access Point with the specified ssid and password.

        If ``channel`` is given, the access point will use that channel unless
        a station is already operating on a different channel.

        If ``authmode`` is given, the access point will use that Authentication
        mode. If a password is given, ``authmode`` must not be ``OPEN``.
        If ``authmode`` isn't given, ``OPEN`` will be used when password isn't provided,
        otherwise ``WPA_WPA2_PSK``.

        If ``max_connections`` is given, the access point will allow up to
        that number of stations to connect."""
        ...
    def stop_ap(self) -> None:
        """Stops the Access Point."""
        ...
    def connect(
        self,
        ssid: Union[str | ReadableBuffer],
        password: Union[str | ReadableBuffer] = "",
        *,
        channel: Optional[int] = 0,
        bssid: Optional[Union[str | ReadableBuffer]] = "",
        timeout: Optional[float] = None,
    ) -> None:
        """Connects to the given ssid and waits for an ip address. Reconnections are handled
        automatically once one connection succeeds.

        By default, this will scan all channels and connect to the access point (AP) with the
        given ``ssid`` and greatest signal strength (rssi).

        If ``channel`` is given, the scan will begin with the given channel and connect to
        the first AP with the given ``ssid``. This can speed up the connection time
        significantly because a full scan doesn't occur.

        If ``bssid`` is given, the scan will start at the first channel or the one given and
        connect to the AP with the given ``bssid`` and ``ssid``."""
        ...
    ipv4_gateway: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the station gateway when connected to an access point. None otherwise."""

    ipv4_gateway_ap: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the access point gateway, when enabled. None otherwise."""

    ipv4_subnet: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the station subnet when connected to an access point. None otherwise."""

    ipv4_subnet_ap: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the access point subnet, when enabled. None otherwise."""

    ipv4_address: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the station when connected to an access point. None otherwise."""

    ipv4_address_ap: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the access point, when enabled. None otherwise."""

    ipv4_dns: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the DNS server in use when connected to an access point. None otherwise."""

    ap_info: Optional[Network]
    """Network object containing BSSID, SSID, authmode, channel, country and RSSI when connected to an access point. None otherwise."""

    def ping(
        self, ip: ipaddress.IPv4Address, *, timeout: Optional[float] = 0.5
    ) -> Optional[float]:
        """Ping an IP to test connectivity. Returns echo time in seconds.
        Returns None when it times out."""
        ...

class ScannedNetworks:
    """Iterates over all `wifi.Network` objects found while scanning. This object is always created
    by a `wifi.Radio`: it has no user-visible constructor."""

    def __init__(self) -> None:
        """Cannot be instantiated directly. Use `wifi.Radio.start_scanning_networks`."""
        ...
    def __iter__(self) -> Iterator[Network]:
        """Returns itself since it is the iterator."""
        ...
    def __next__(self) -> Network:
        """Returns the next `wifi.Network`.
        Raises `StopIteration` if scanning is finished and no other results are available."""
        ...
