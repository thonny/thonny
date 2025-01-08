"""
The `socketpool` module provides sockets through a pool. The pools themselves
act like CPython's `socket` module.

For more information about the `socket` module, see the CPython documentation:
https://docs.python.org/3/library/socket.html

.. jinja

.. raw:: html

    <p>
    <details>
    <summary>AF_INET6 (IPv6) supported on these boards</summary>
    <ul>
    {% for board in support_matrix_reverse["socketpool.socketpool.AF_INET6"] %}
    <li> {{ board }}
    {% endfor %}
    </ul>
    </details>
    </p>
"""

from __future__ import annotations

from typing import Optional, Tuple

import socketpool
import wifi
from circuitpython_typing import ReadableBuffer, WriteableBuffer

class Socket:
    """TCP, UDP and RAW socket. Cannot be created directly. Instead, call
    `SocketPool.socket()`.

    Provides a subset of CPython's `socket.socket` API. It only implements the versions of
    recv that do not allocate bytes objects."""

    def __hash__(self) -> int:
        """Returns a hash for the Socket."""
        ...

    def __enter__(self) -> Socket:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically closes the Socket when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def accept(self) -> Tuple[Socket, Tuple[str, int]]:
        """Accept a connection on a listening socket of type SOCK_STREAM,
        creating a new socket of type SOCK_STREAM.
        Returns a tuple of (new_socket, remote_address)"""

    def bind(self, address: Tuple[str, int]) -> None:
        """Bind a socket to an address

        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def close(self) -> None:
        """Closes this Socket and makes its resources available to its SocketPool."""

    def connect(self, address: Tuple[str, int]) -> None:
        """Connect a socket to a remote address

        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def listen(self, backlog: int) -> None:
        """Set socket to listen for incoming connections

        :param ~int backlog: length of backlog queue for waiting connections"""
        ...

    def recvfrom_into(self, buffer: WriteableBuffer) -> Tuple[int, Tuple[str, int]]:
        """Reads some bytes from a remote address.

        Returns a tuple containing
        * the number of bytes received into the given buffer
        * a remote_address, which is a tuple of ip address and port number

        :param object buffer: buffer to read into"""
        ...

    def recv_into(self, buffer: WriteableBuffer, bufsize: int) -> int:
        """Reads some bytes from the connected remote address, writing
        into the provided buffer. If bufsize <= len(buffer) is given,
        a maximum of bufsize bytes will be read into the buffer. If no
        valid value is given for bufsize, the default is the length of
        the given buffer.

        Suits sockets of type SOCK_STREAM
        Returns an int of number of bytes read.

        :param bytearray buffer: buffer to receive into
        :param int bufsize: optionally, a maximum number of bytes to read."""
        ...

    def send(self, bytes: ReadableBuffer) -> int:
        """Send some bytes to the connected remote address.
        Suits sockets of type SOCK_STREAM

        :param ~bytes bytes: some bytes to send"""
        ...

    def sendall(self, bytes: ReadableBuffer) -> None:
        """Send some bytes to the connected remote address.
        Suits sockets of type SOCK_STREAM

        This calls send() repeatedly until all the data is sent or an error
        occurs. If an error occurs, it's impossible to tell how much data
        has been sent.

        :param ~bytes bytes: some bytes to send"""
        ...

    def sendto(self, bytes: ReadableBuffer, address: Tuple[str, int]) -> int:
        """Send some bytes to a specific address.
        Suits sockets of type SOCK_DGRAM

        :param ~bytes bytes: some bytes to send
        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def setblocking(self, flag: bool) -> Optional[int]:
        """Set the blocking behaviour of this socket.

        :param ~bool flag: False means non-blocking, True means block indefinitely."""
        ...

    def setsockopt(self, level: int, optname: int, value: int) -> None:
        """Sets socket options"""
        ...

    def settimeout(self, value: int) -> None:
        """Set the timeout value for this socket.

        :param ~int value: timeout in seconds.  0 means non-blocking.  None means block indefinitely.
        """
        ...
    type: int
    """Read-only access to the socket type"""

class SocketPool:
    """A pool of socket resources available for the given radio. Only one
    SocketPool can be created for each radio.

    SocketPool should be used in place of CPython's socket which provides
    a pool of sockets provided by the underlying OS.
    """

    def __init__(self, radio: wifi.Radio) -> None:
        """Create a new SocketPool object for the provided radio

        :param wifi.Radio radio: The (connected) network hardware to associate
            with this SocketPool; currently, this will always be the object
            returned by :py:attr:`wifi.radio`
        """
        ...

    class gaierror(OSError):
        """Errors raised by getaddrinfo"""

    AF_INET: int
    AF_INET6: int

    SOCK_STREAM: int
    SOCK_DGRAM: int
    SOCK_RAW: int
    EAI_NONAME: int

    SOL_SOCKET: int

    SO_REUSEADDR: int

    TCP_NODELAY: int

    IPPROTO_IP: int
    IPPROTO_ICMP: int
    IPPROTO_TCP: int
    IPPROTO_UDP: int
    IPPROTO_IPV6: int
    IPPROTO_RAW: int

    IP_MULTICAST_TTL: int

    def socket(
        self, family: int = AF_INET, type: int = SOCK_STREAM, proto: int = IPPROTO_IP
    ) -> socketpool.Socket:
        """Create a new socket

        :param ~int family: AF_INET or AF_INET6
        :param ~int type: SOCK_STREAM, SOCK_DGRAM or SOCK_RAW
        :param ~int proto: IPPROTO_IP, IPPROTO_ICMP, IPPROTO_TCP, IPPROTO_UDP, IPPROTO_IPV6or IPPROTO_RAW. Only works with SOCK_RAW

        The ``fileno`` argument available in ``socket.socket()``
        in CPython is not supported.
        """
        ...

    def getaddrinfo(
        self,
        host: str,
        port: int,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> Tuple[int, int, int, str, Tuple[str, int]]:
        """Gets the address information for a hostname and port

        Returns the appropriate family, socket type, socket protocol and
        address information to call socket.socket() and socket.connect() with,
        as a tuple."""
        ...
