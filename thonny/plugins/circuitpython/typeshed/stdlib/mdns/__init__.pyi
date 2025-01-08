"""Multicast Domain Name Service

The `mdns` module provides basic support for multicast domain name services.
Basic use provides hostname resolution under the .local TLD. This module
also supports DNS Service Discovery that allows for discovering other hosts
that provide a desired service."""

from __future__ import annotations

import ipaddress
from typing import Optional, Tuple

import wifi

class RemoteService:
    """Encapsulates information about a remote service that was found during a search. This
    object may only be created by a `mdns.Server`. It has no user-visible constructor.
    """

    def __init__(self) -> None:
        """Cannot be instantiated directly. Use `mdns.Server.find`."""
        ...
    hostname: str
    """The hostname of the device (read-only),."""
    instance_name: str
    """The human readable instance name for the service. (read-only)"""
    service_type: str
    """The service type string such as ``_http``. (read-only)"""
    protocol: str
    """The protocol string such as ``_tcp``. (read-only)"""
    port: int
    """Port number used for the service. (read-only)"""
    ipv4_address: Optional[ipaddress.IPv4Address]
    """IP v4 Address of the remote service. None if no A records are found."""
    def __del__(self) -> None:
        """Deletes the RemoteService object."""
        ...

class Server:
    """The MDNS Server responds to queries for this device's information and allows for querying
    other devices."""

    def __init__(self, network_interface: wifi.Radio) -> None:
        """
        Constructs or returns the mdns.Server for the given network_interface. (CircuitPython
        may already be using it.) Only native interfaces are currently supported.
        """
        ...

    def deinit(self) -> None:
        """Stops the server"""
        ...
    hostname: str
    """Hostname resolvable as ``<hostname>.local`` in addition to ``circuitpython.local``. Make
       sure this is unique across all devices on the network. It defaults to ``cpy-######``
       where ``######`` is the hex digits of the last three bytes of the mac address."""
    instance_name: str
    """Human readable name to describe the device."""
    def find(
        self, service_type: str, protocol: str, *, timeout: float = 1
    ) -> Tuple[RemoteService]:
        """Find all locally available remote services with the given service type and protocol.

        This doesn't allow for direct hostname lookup. To do that, use
        `socketpool.SocketPool.getaddrinfo()`.

        :param str service_type: The service type such as "_http"
        :param str protocol: The service protocol such as "_tcp"
        :param float/int timeout: Time to wait for responses"""
        ...

    def advertise_service(self, *, service_type: str, protocol: str, port: int) -> None:
        """Respond to queries for the given service with the given port.

        ``service_type`` and ``protocol`` can only occur on one port. Any call after the first
        will update the entry's port.

        If web workflow is active, the port it uses can't also be used to advertise a service.

        **Limitations**: Publishing up to 32 TXT records is only supported on the RP2040 Pico W board at
        this time.

        :param str service_type: The service type such as "_http"
        :param str protocol: The service protocol such as "_tcp"
        :param int port: The port used by the service
        :param Sequence[str] txt_records: An optional sequence of strings to serve as TXT records along with the service
        """
        ...
