"""
The `ssl` module provides SSL contexts to wrap sockets in.

|see_cpython_module| :mod:`cpython:ssl`.
"""

from __future__ import annotations

import ssl
from typing import Optional, Tuple

import socketpool
from circuitpython_typing import ReadableBuffer, WriteableBuffer

def create_default_context() -> ssl.SSLContext:
    """Return the default SSLContext."""
    ...

class SSLContext:
    """Settings related to SSL that can be applied to a socket by wrapping it.
    This is useful to provide SSL certificates to specific connections
    rather than all of them."""

    def load_cert_chain(self, certfile: str, keyfile: str) -> None:
        """Load a private key and the corresponding certificate.

        The certfile string must be the path to a single file in PEM format
        containing the certificate as well as any number of CA certificates
        needed to establish the certificate's authenticity.  The keyfile string
        must point to a file containing the private key.
        """

    def load_verify_locations(
        self,
        cafile: Optional[str] = None,
        capath: Optional[str] = None,
        cadata: Optional[str] = None,
    ) -> None:
        """
        Load a set of certification authority (CA) certificates used to validate
        other peers' certificates.

        :param str cafile: path to a file of contcatenated CA certificates in PEM format. **Not implemented**.
        :param str capath: path to a directory of CA certificate files in PEM format. **Not implemented**.
        :param str cadata: A single CA certificate in PEM format. **Limitation**: CPython allows one
          or more certificates, but this implementation is limited to one.
        """

    def set_default_verify_paths(self) -> None:
        """Load a set of default certification authority (CA) certificates."""
    check_hostname: bool
    """Whether to match the peer certificate's hostname."""

    def wrap_socket(
        self,
        sock: socketpool.Socket,
        *,
        server_side: bool = False,
        server_hostname: Optional[str] = None,
    ) -> ssl.SSLSocket:
        """Wraps the socket into a socket-compatible class that handles SSL negotiation.
        The socket must be of type SOCK_STREAM."""

class SSLSocket:
    """Implements TLS security on a subset of `socketpool.Socket` functions. Cannot be created
    directly. Instead, call `wrap_socket` on an existing socket object.

    Provides a subset of CPython's `ssl.SSLSocket` API. It only implements the versions of
    recv that do not allocate bytes objects."""

    def __hash__(self) -> int:
        """Returns a hash for the Socket."""
        ...

    def __enter__(self) -> SSLSocket:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically closes the Socket when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def accept(self) -> Tuple[SSLSocket, Tuple[str, int]]:
        """Accept a connection on a listening socket of type SOCK_STREAM,
        creating a new socket of type SOCK_STREAM.
        Returns a tuple of (new_socket, remote_address)"""

    def bind(self, address: Tuple[str, int]) -> None:
        """Bind a socket to an address

        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def close(self) -> None:
        """Closes this Socket"""

    def connect(self, address: Tuple[str, int]) -> None:
        """Connect a socket to a remote address

        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def listen(self, backlog: int) -> None:
        """Set socket to listen for incoming connections

        :param ~int backlog: length of backlog queue for waiting connetions"""
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

    def settimeout(self, value: int) -> None:
        """Set the timeout value for this socket.

        :param ~int value: timeout in seconds.  0 means non-blocking.  None means block indefinitely.
        """
        ...

    def setblocking(self, flag: bool) -> Optional[int]:
        """Set the blocking behaviour of this socket.

        :param ~bool flag: False means non-blocking, True means block indefinitely."""
        ...
