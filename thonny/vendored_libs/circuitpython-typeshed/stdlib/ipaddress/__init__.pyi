"""
The `ipaddress` module provides types for IP addresses. It is a subset of CPython's ipaddress
module.
"""

from __future__ import annotations

from typing import Union

def ip_address(obj: Union[int, str]) -> IPv4Address:
    """Return a corresponding IP address object or raise ValueError if not possible."""
    ...

class IPv4Address:
    """Encapsulates an IPv4 address."""

    def __init__(self, address: Union[int, str, bytes]) -> None:
        """Create a new IPv4Address object encapsulating the address value.

        The value itself can either be bytes or a string formatted address."""
        ...
    packed: bytes
    """The bytes that make up the address (read-only)."""
    version: int
    """4 for IPv4, 6 for IPv6"""

    def __eq__(self, other: object) -> bool:
        """Two Address objects are equal if their addresses and address types are equal."""
        ...

    def __hash__(self) -> int:
        """Returns a hash for the IPv4Address data."""
        ...
