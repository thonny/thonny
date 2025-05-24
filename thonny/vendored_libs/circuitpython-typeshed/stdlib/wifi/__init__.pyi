"""
The `wifi` module provides necessary low-level functionality for managing
wifi connections. Use `socketpool` for communicating over the network.
"""

from __future__ import annotations

import ipaddress
from typing import Iterable, Iterator, Optional, Sequence, Union

import wifi
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
    authmode: Sequence[wifi.AuthMode]
    """List of authmodes (wifi.AuthMode) used by the network """

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
       the changes would only be reflected once the interface reconnects.

    **Limitations:** Not settable on RP2040 CYW43 boards, such as Pi Pico W.
    """
    tx_power: float
    """Wifi transmission power, in dBm."""
    listen_interval: int
    """Wifi power save listen interval, in DTIM periods, or 100ms intervals if TWT is supported."""
    mac_address_ap: ReadableBuffer
    """MAC address for the AP. When the address is altered after interface is started
       the changes would only be reflected once the interface restarts.

    **Limitations:** Not settable on RP2040 CYW43 boards, such as Pi Pico W.
    """

    def start_scanning_networks(
        self, *, start_channel: int = 1, stop_channel: int = 11
    ) -> Iterable[Network]:
        """Scans for available wifi networks over the given channel range. Make sure the channels are allowed in your country.

        .. note::

            In the raspberrypi port (RP2040 CYW43), ``start_channel`` and ``stop_channel`` are ignored.
        """
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
        password: Union[str | ReadableBuffer] = b"",
        *,
        channel: int = 1,
        authmode: Iterable[AuthMode] = (),
        max_connections: Optional[int] = 4,
    ) -> None:
        """Starts running an access point with the specified ssid and password.

        If ``channel`` is given, the access point will use that channel unless
        a station is already operating on a different channel.

        If ``authmode`` is not None, the access point will use the given authentication modes.
        If a non-empty password is given, ``authmode`` must not include ``OPEN``.
        If ``authmode`` is not given or is an empty iterable,
        ``(wifi.AuthMode.OPEN,)`` will be used when the password is the empty string,
        otherwise ``authmode`` will be ``(wifi.AuthMode.WPA, wifi.AuthMode.WPA2, wifi.AuthMode.PSK)``.

        **Limitations:** On Espressif, ``authmode`` with a non-empty password must include
        `wifi.AuthMode.PSK`, and one or both of `wifi.AuthMode.WPA` and `wifi.AuthMode.WPA2`.
        On Pi Pico W, ``authmode`` is ignored; it is always ``(wifi.AuthMode.WPA2, wifi.AuthMode.PSK)``
        with a non-empty password, or ``(wifi.AuthMode.OPEN)``, when no password is given.
        On Pi Pico W, the AP can be started and stopped only once per reboot.

        The length of ``password`` must be 8-63 characters if it is ASCII,
        or exactly 64 hexadecimal characters if it is the hex form of the 256-bit key.

        If ``max_connections`` is given, the access point will allow up to
        that number of stations to connect.

        .. note::

            In the raspberrypi port (RP2040 CYW43), ``max_connections`` is ignored.
        """
        ...

    def stop_ap(self) -> None:
        """Stops the access point."""
        ...
    ap_active: bool
    """True if running as an access point. (read-only)"""

    def connect(
        self,
        ssid: Union[str | ReadableBuffer],
        password: Union[str | ReadableBuffer] = b"",
        *,
        channel: int = 0,
        bssid: Optional[Union[str | ReadableBuffer]] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """Connects to the given ssid and waits for an ip address. Reconnections are handled
        automatically once one connection succeeds.

        The length of ``password`` must be 0 if there is no password, 8-63 characters if it is ASCII,
        or exactly 64 hexadecimal characters if it is the hex form of the 256-bit key.

        By default, this will scan all channels and connect to the access point (AP) with the
        given ``ssid`` and greatest signal strength (rssi).

        If ``channel`` is non-zero, the scan will begin with the given channel and connect to
        the first AP with the given ``ssid``. This can speed up the connection time
        significantly because a full scan doesn't occur.

        If ``bssid`` is given and not None, the scan will start at the first channel or the one given and
        connect to the AP with the given ``bssid`` and ``ssid``."""
        ...
    connected: bool
    """True if connected to an access point (read-only)."""
    ipv4_gateway: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the station gateway when connected to an access point. None otherwise. (read-only)"""
    ipv4_gateway_ap: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the access point gateway, when enabled. None otherwise. (read-only)"""
    ipv4_subnet: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the station subnet when connected to an access point. None otherwise. (read-only)"""
    ipv4_subnet_ap: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the access point subnet, when enabled. None otherwise. (read-only)"""

    def set_ipv4_address(
        self,
        *,
        ipv4: ipaddress.IPv4Address,
        netmask: ipaddress.IPv4Address,
        gateway: ipaddress.IPv4Address,
        ipv4_dns: Optional[ipaddress.IPv4Address],
    ) -> None:
        """Sets the IP v4 address of the station. Must include the netmask and gateway. DNS address is optional.
        Setting the address manually will stop the DHCP client.

        .. note::

            In the raspberrypi port (RP2040 CYW43), the access point needs to be started before the IP v4 address can be set.
        """
        ...

    def set_ipv4_address_ap(
        self,
        *,
        ipv4: ipaddress.IPv4Address,
        netmask: ipaddress.IPv4Address,
        gateway: ipaddress.IPv4Address,
    ) -> None:
        """Sets the IP v4 address of the access point. Must include the netmask and gateway."""
        ...
    addresses: Sequence[str]
    """Address(es) of the station when connected to an access point. Empty sequence when not connected. (read-only)"""
    addresses_ap: Sequence[str]
    """Address(es) of the access point when enabled. Empty sequence when disabled. (read-only)"""
    ipv4_address: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the station when connected to an access point. None otherwise. (read-only)"""
    ipv4_address_ap: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the access point, when enabled. None otherwise. (read-only)"""
    ipv4_dns: ipaddress.IPv4Address
    """IP v4 Address of the DNS server to be used."""
    dns: Sequence[str]
    """Address of the DNS server to be used."""
    ap_info: Optional[Network]
    """Network object containing BSSID, SSID, authmode, channel, country and RSSI when connected to an access point. None otherwise."""
    stations_ap: None
    """In AP mode, returns list of named tuples, each of which contains:
     mac: bytearray (read-only)
     rssi: int (read-only, None on Raspberry Pi Pico W)
     ipv4_address: ipv4_address  (read-only, None if station connected but no address assigned yet or self-assigned address)"""

    def start_dhcp(self, *, ipv4: bool = True, ipv6: bool = False) -> None:
        """Starts the station DHCP client.

        By default, calling this function starts DHCP for IPv4 networks but not
        IPv6 networks. When the the ``ipv4`` and ``ipv6`` arguments are `False`
        then the corresponding DHCP client is stopped if it was active.
        """
        ...

    def stop_dhcp(self) -> None:
        """Stops the station DHCP client. Needed to assign a static IP address."""
        ...

    def start_dhcp_ap(self) -> None:
        """Starts the access point DHCP server."""
        ...

    def stop_dhcp_ap(self) -> None:
        """Stops the access point DHCP server. Needed to assign a static IP address."""
        ...

    def ping(
        self, ip: ipaddress.IPv4Address, *, timeout: Optional[float] = 0.5
    ) -> Optional[float]:
        """Ping an IP to test connectivity. Returns echo time in seconds.
        Returns None when it times out.

        **Limitations:** On Espressif, calling `ping()` multiple times rapidly
        exhausts available resources after several calls. Rather than failing at that point, `ping()`
        will wait two seconds for enough resources to be freed up before proceeding.
        """
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
        Raises `StopIteration` if scanning is finished and no other results are available.
        """
        ...
