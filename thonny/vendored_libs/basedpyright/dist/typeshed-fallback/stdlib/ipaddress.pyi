import sys
from collections.abc import Iterable, Iterator
from typing import Any, Final, Generic, Literal, TypeVar, overload
from typing_extensions import Self, TypeAlias

# Undocumented length constants
IPV4LENGTH: Final = 32
IPV6LENGTH: Final = 128

_A = TypeVar("_A", IPv4Address, IPv6Address)
_N = TypeVar("_N", IPv4Network, IPv6Network)

_RawIPAddress: TypeAlias = int | str | bytes | IPv4Address | IPv6Address
_RawNetworkPart: TypeAlias = IPv4Network | IPv6Network | IPv4Interface | IPv6Interface

def ip_address(address: _RawIPAddress) -> IPv4Address | IPv6Address: ...
def ip_network(
    address: _RawIPAddress | _RawNetworkPart | tuple[_RawIPAddress] | tuple[_RawIPAddress, int], strict: bool = True
) -> IPv4Network | IPv6Network: ...
def ip_interface(
    address: _RawIPAddress | _RawNetworkPart | tuple[_RawIPAddress] | tuple[_RawIPAddress, int],
) -> IPv4Interface | IPv6Interface: ...

class _IPAddressBase:
    @property
    def compressed(self) -> str:
        """Return the shorthand version of the IP address as a string."""
        ...
    @property
    def exploded(self) -> str:
        """Return the longhand version of the IP address as a string."""
        ...
    @property
    def reverse_pointer(self) -> str:
        """
        The name of the reverse DNS pointer for the IP address, e.g.:
        >>> ipaddress.ip_address("127.0.0.1").reverse_pointer
        '1.0.0.127.in-addr.arpa'
        >>> ipaddress.ip_address("2001:db8::1").reverse_pointer
        '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'
        """
        ...
    @property
    def version(self) -> int: ...

class _BaseAddress(_IPAddressBase):
    def __add__(self, other: int) -> Self: ...
    def __hash__(self) -> int: ...
    def __int__(self) -> int: ...
    def __sub__(self, other: int) -> Self: ...
    def __format__(self, fmt: str) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __lt__(self, other: Self) -> bool: ...
    if sys.version_info >= (3, 11):
        def __ge__(self, other: Self) -> bool: ...
        def __gt__(self, other: Self) -> bool: ...
        def __le__(self, other: Self) -> bool: ...
    else:
        def __ge__(self, other: Self, NotImplemented: Any = ...) -> bool: ...
        def __gt__(self, other: Self, NotImplemented: Any = ...) -> bool: ...
        def __le__(self, other: Self, NotImplemented: Any = ...) -> bool: ...

class _BaseNetwork(_IPAddressBase, Generic[_A]):
    network_address: _A
    netmask: _A
    def __contains__(self, other: Any) -> bool: ...
    def __getitem__(self, n: int) -> _A: ...
    def __iter__(self) -> Iterator[_A]: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __lt__(self, other: Self) -> bool: ...
    if sys.version_info >= (3, 11):
        def __ge__(self, other: Self) -> bool: ...
        def __gt__(self, other: Self) -> bool: ...
        def __le__(self, other: Self) -> bool: ...
    else:
        def __ge__(self, other: Self, NotImplemented: Any = ...) -> bool: ...
        def __gt__(self, other: Self, NotImplemented: Any = ...) -> bool: ...
        def __le__(self, other: Self, NotImplemented: Any = ...) -> bool: ...

    def address_exclude(self, other: Self) -> Iterator[Self]: ...
    @property
    def broadcast_address(self) -> _A: ...
    def compare_networks(self, other: Self) -> int: ...
    def hosts(self) -> Iterator[_A]: ...
    @property
    def is_global(self) -> bool:
        """
        Test if this address is allocated for public networks.

        Returns:
            A boolean, True if the address is not reserved per
            iana-ipv4-special-registry or iana-ipv6-special-registry.
        """
        ...
    @property
    def is_link_local(self) -> bool:
        """
        Test if the address is reserved for link-local.

        Returns:
            A boolean, True if the address is reserved per RFC 4291.
        """
        ...
    @property
    def is_loopback(self) -> bool:
        """
        Test if the address is a loopback address.

        Returns:
            A boolean, True if the address is a loopback address as defined in
            RFC 2373 2.5.3.
        """
        ...
    @property
    def is_multicast(self) -> bool:
        """
        Test if the address is reserved for multicast use.

        Returns:
            A boolean, True if the address is a multicast address.
            See RFC 2373 2.7 for details.
        """
        ...
    @property
    def is_private(self) -> bool:
        """
        Test if this network belongs to a private range.

        Returns:
            A boolean, True if the network is reserved per
            iana-ipv4-special-registry or iana-ipv6-special-registry.
        """
        ...
    @property
    def is_reserved(self) -> bool:
        """
        Test if the address is otherwise IETF reserved.

        Returns:
            A boolean, True if the address is within one of the
            reserved IPv6 Network ranges.
        """
        ...
    @property
    def is_unspecified(self) -> bool:
        """
        Test if the address is unspecified.

        Returns:
            A boolean, True if this is the unspecified address as defined in
            RFC 2373 2.5.2.
        """
        ...
    @property
    def num_addresses(self) -> int:
        """Number of hosts in the current subnet."""
        ...
    def overlaps(self, other: _BaseNetwork[IPv4Address] | _BaseNetwork[IPv6Address]) -> bool: ...
    @property
    def prefixlen(self) -> int: ...
    def subnet_of(self, other: Self) -> bool: ...
    def supernet_of(self, other: Self) -> bool: ...
    def subnets(self, prefixlen_diff: int = 1, new_prefix: int | None = None) -> Iterator[Self]: ...
    def supernet(self, prefixlen_diff: int = 1, new_prefix: int | None = None) -> Self: ...
    @property
    def with_hostmask(self) -> str: ...
    @property
    def with_netmask(self) -> str: ...
    @property
    def with_prefixlen(self) -> str: ...
    @property
    def hostmask(self) -> _A: ...

class _BaseV4:
    @property
    def version(self) -> Literal[4]: ...
    @property
    def max_prefixlen(self) -> Literal[32]: ...

class IPv4Address(_BaseV4, _BaseAddress):
    def __init__(self, address: object) -> None: ...
    @property
    def is_global(self) -> bool:
        """
        ``True`` if the address is defined as globally reachable by
        iana-ipv4-special-registry_ (for IPv4) or iana-ipv6-special-registry_
        (for IPv6) with the following exception:

        For IPv4-mapped IPv6-addresses the ``is_private`` value is determined by the
        semantics of the underlying IPv4 addresses and the following condition holds
        (see :attr:`IPv6Address.ipv4_mapped`)::

            address.is_global == address.ipv4_mapped.is_global

        ``is_global`` has value opposite to :attr:`is_private`, except for the ``100.64.0.0/10``
        IPv4 range where they are both ``False``.
        """
        ...
    @property
    def is_link_local(self) -> bool:
        """
        Test if the address is reserved for link-local.

        Returns:
            A boolean, True if the address is link-local per RFC 3927.
        """
        ...
    @property
    def is_loopback(self) -> bool:
        """
        Test if the address is a loopback address.

        Returns:
            A boolean, True if the address is a loopback per RFC 3330.
        """
        ...
    @property
    def is_multicast(self) -> bool:
        """
        Test if the address is reserved for multicast use.

        Returns:
            A boolean, True if the address is multicast.
            See RFC 3171 for details.
        """
        ...
    @property
    def is_private(self) -> bool:
        """
        ``True`` if the address is defined as not globally reachable by
        iana-ipv4-special-registry_ (for IPv4) or iana-ipv6-special-registry_
        (for IPv6) with the following exceptions:

        * ``is_private`` is ``False`` for ``100.64.0.0/10``
        * For IPv4-mapped IPv6-addresses the ``is_private`` value is determined by the
            semantics of the underlying IPv4 addresses and the following condition holds
            (see :attr:`IPv6Address.ipv4_mapped`)::

                address.is_private == address.ipv4_mapped.is_private

        ``is_private`` has value opposite to :attr:`is_global`, except for the ``100.64.0.0/10``
        IPv4 range where they are both ``False``.
        """
        ...
    @property
    def is_reserved(self) -> bool:
        """
        Test if the address is otherwise IETF reserved.

        Returns:
            A boolean, True if the address is within the
            reserved IPv4 Network range.
        """
        ...
    @property
    def is_unspecified(self) -> bool:
        """
        Test if the address is unspecified.

        Returns:
            A boolean, True if this is the unspecified address as defined in
            RFC 5735 3.
        """
        ...
    @property
    def packed(self) -> bytes:
        """The binary representation of this address."""
        ...
    if sys.version_info >= (3, 13):
        @property
        def ipv6_mapped(self) -> IPv6Address:
            """
            Return the IPv4-mapped IPv6 address.

            Returns:
                The IPv4-mapped IPv6 address per RFC 4291.
            """
            ...

class IPv4Network(_BaseV4, _BaseNetwork[IPv4Address]):
    def __init__(self, address: object, strict: bool = ...) -> None: ...

class IPv4Interface(IPv4Address):
    netmask: IPv4Address
    network: IPv4Network
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def hostmask(self) -> IPv4Address: ...
    @property
    def ip(self) -> IPv4Address: ...
    @property
    def with_hostmask(self) -> str: ...
    @property
    def with_netmask(self) -> str: ...
    @property
    def with_prefixlen(self) -> str: ...

class _BaseV6:
    @property
    def version(self) -> Literal[6]: ...
    @property
    def max_prefixlen(self) -> Literal[128]: ...

class IPv6Address(_BaseV6, _BaseAddress):
    def __init__(self, address: object) -> None: ...
    @property
    def is_global(self) -> bool:
        """
        ``True`` if the address is defined as globally reachable by
        iana-ipv4-special-registry_ (for IPv4) or iana-ipv6-special-registry_
        (for IPv6) with the following exception:

        For IPv4-mapped IPv6-addresses the ``is_private`` value is determined by the
        semantics of the underlying IPv4 addresses and the following condition holds
        (see :attr:`IPv6Address.ipv4_mapped`)::

            address.is_global == address.ipv4_mapped.is_global

        ``is_global`` has value opposite to :attr:`is_private`, except for the ``100.64.0.0/10``
        IPv4 range where they are both ``False``.
        """
        ...
    @property
    def is_link_local(self) -> bool:
        """
        Test if the address is reserved for link-local.

        Returns:
            A boolean, True if the address is reserved per RFC 4291.
        """
        ...
    @property
    def is_loopback(self) -> bool:
        """
        Test if the address is a loopback address.

        Returns:
            A boolean, True if the address is a loopback address as defined in
            RFC 2373 2.5.3.
        """
        ...
    @property
    def is_multicast(self) -> bool:
        """
        Test if the address is reserved for multicast use.

        Returns:
            A boolean, True if the address is a multicast address.
            See RFC 2373 2.7 for details.
        """
        ...
    @property
    def is_private(self) -> bool:
        """
        ``True`` if the address is defined as not globally reachable by
        iana-ipv4-special-registry_ (for IPv4) or iana-ipv6-special-registry_
        (for IPv6) with the following exceptions:

        * ``is_private`` is ``False`` for ``100.64.0.0/10``
        * For IPv4-mapped IPv6-addresses the ``is_private`` value is determined by the
            semantics of the underlying IPv4 addresses and the following condition holds
            (see :attr:`IPv6Address.ipv4_mapped`)::

                address.is_private == address.ipv4_mapped.is_private

        ``is_private`` has value opposite to :attr:`is_global`, except for the ``100.64.0.0/10``
        IPv4 range where they are both ``False``.
        """
        ...
    @property
    def is_reserved(self) -> bool:
        """
        Test if the address is otherwise IETF reserved.

        Returns:
            A boolean, True if the address is within one of the
            reserved IPv6 Network ranges.
        """
        ...
    @property
    def is_unspecified(self) -> bool:
        """
        Test if the address is unspecified.

        Returns:
            A boolean, True if this is the unspecified address as defined in
            RFC 2373 2.5.2.
        """
        ...
    @property
    def packed(self) -> bytes:
        """The binary representation of this address."""
        ...
    @property
    def ipv4_mapped(self) -> IPv4Address | None:
        """
        Return the IPv4 mapped address.

        Returns:
            If the IPv6 address is a v4 mapped address, return the
            IPv4 mapped address. Return None otherwise.
        """
        ...
    @property
    def is_site_local(self) -> bool:
        """
        Test if the address is reserved for site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test if this address is in the space of unique local
        addresses as defined by RFC 4193.

        Returns:
            A boolean, True if the address is reserved per RFC 3513 2.5.6.
        """
        ...
    @property
    def sixtofour(self) -> IPv4Address | None:
        """
        Return the IPv4 6to4 embedded address.

        Returns:
            The IPv4 6to4-embedded address if present or None if the
            address doesn't appear to contain a 6to4 embedded address.
        """
        ...
    @property
    def teredo(self) -> tuple[IPv4Address, IPv4Address] | None:
        """
        Tuple of embedded teredo IPs.

        Returns:
            Tuple of the (server, client) IPs or None if the address
            doesn't appear to be a teredo address (doesn't start with
            2001::/32)
        """
        ...
    @property
    def scope_id(self) -> str | None:
        """
        Identifier of a particular zone of the address's scope.

        See RFC 4007 for details.

        Returns:
            A string identifying the zone of the address if specified, else None.
        """
        ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...

class IPv6Network(_BaseV6, _BaseNetwork[IPv6Address]):
    def __init__(self, address: object, strict: bool = ...) -> None: ...
    @property
    def is_site_local(self) -> bool:
        """
        Test if the address is reserved for site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test if this address is in the space of unique local
        addresses as defined by RFC 4193.

        Returns:
            A boolean, True if the address is reserved per RFC 3513 2.5.6.
        """
        ...

class IPv6Interface(IPv6Address):
    netmask: IPv6Address
    network: IPv6Network
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def hostmask(self) -> IPv6Address: ...
    @property
    def ip(self) -> IPv6Address: ...
    @property
    def with_hostmask(self) -> str: ...
    @property
    def with_netmask(self) -> str: ...
    @property
    def with_prefixlen(self) -> str: ...

def v4_int_to_packed(address: int) -> bytes: ...
def v6_int_to_packed(address: int) -> bytes: ...

# Third overload is technically incorrect, but convenient when first and last are return values of ip_address()
@overload
def summarize_address_range(first: IPv4Address, last: IPv4Address) -> Iterator[IPv4Network]: ...
@overload
def summarize_address_range(first: IPv6Address, last: IPv6Address) -> Iterator[IPv6Network]: ...
@overload
def summarize_address_range(
    first: IPv4Address | IPv6Address, last: IPv4Address | IPv6Address
) -> Iterator[IPv4Network] | Iterator[IPv6Network]: ...
def collapse_addresses(addresses: Iterable[_N]) -> Iterator[_N]: ...
@overload
def get_mixed_type_key(obj: _A) -> tuple[int, _A]: ...
@overload
def get_mixed_type_key(obj: IPv4Network) -> tuple[int, IPv4Address, IPv4Address]: ...
@overload
def get_mixed_type_key(obj: IPv6Network) -> tuple[int, IPv6Address, IPv6Address]: ...

class AddressValueError(ValueError): ...
class NetmaskValueError(ValueError): ...
