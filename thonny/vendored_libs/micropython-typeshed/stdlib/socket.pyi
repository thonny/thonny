"""
Socket module.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/socket.html

CPython module: :mod:`python:socket` https://docs.python.org/3/library/socket.html .

This module provides access to the BSD socket interface.

Admonition:Difference to CPython
   :class: attention

   For efficiency and consistency, socket objects in MicroPython implement a `stream`
   (file-like) interface directly. In CPython, you need to convert a socket to
   a file-like object using `makefile()` method. This method is still supported
   by MicroPython (but is a no-op), so where compatibility with CPython matters,
   be sure to use it.

Socket address format(s)
------------------------

The native socket address format of the ``socket`` module is an opaque data type
returned by `getaddrinfo` function, which must be used to resolve textual address
(including numeric addresses)::

    sockaddr = socket.getaddrinfo('www.micropython.org', 80)[0][-1]
    # You must use getaddrinfo() even for numeric addresses
    sockaddr = socket.getaddrinfo('127.0.0.1', 80)[0][-1]
    # Now you can use that address
    sock.connect(sockaddr)

Using `getaddrinfo` is the most efficient (both in terms of memory and processing
power) and portable way to work with addresses.

However, ``socket`` module (note the difference with native MicroPython
``socket`` module described here) provides CPython-compatible way to specify
addresses using tuples, as described below. Note that depending on a
:term:`MicroPython port`, ``socket`` module can be builtin or need to be
installed from `micropython-lib` (as in the case of :term:`MicroPython Unix port`),
and some ports still accept only numeric addresses in the tuple format,
and require to use `getaddrinfo` function to resolve domain names.

Summing up:

* Always use `getaddrinfo` when writing portable applications.
* Tuple addresses described below can be used as a shortcut for
  quick hacks and interactive use, if your port supports them.

Tuple address format for ``socket`` module:

* IPv4: *(ipv4_address, port)*, where *ipv4_address* is a string with
  dot-notation numeric IPv4 address, e.g. ``"8.8.8.8"``, and *port* is and
  integer port number in the range 1-65535. Note the domain names are not
  accepted as *ipv4_address*, they should be resolved first using
  `socket.getaddrinfo()`.
* IPv6: *(ipv6_address, port, flowinfo, scopeid)*, where *ipv6_address*
  is a string with colon-notation numeric IPv6 address, e.g. ``"2001:db8::1"``,
  and *port* is an integer port number in the range 1-65535. *flowinfo*
  must be 0. *scopeid* is the interface scope identifier for link-local
  addresses. Note the domain names are not accepted as *ipv6_address*,
  they should be resolved first using `socket.getaddrinfo()`. Availability
  of IPv6 support depends on a :term:`MicroPython port`.

---
Module: 'socket' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import Literal, Tuple, overload, Final
from _typeshed import Incomplete
from _mpy_shed import AnyReadableBuf, AnyWritableBuf
from typing_extensions import Awaitable, TypeAlias, TypeVar

SOCK_STREAM: Final[int] = 1
SOL_SOCKET: Final[int] = 4095
SOCK_RAW: Final[int] = 3
TCP_NODELAY: Final[int] = 1
SO_REUSEADDR: Final[int] = 4
SO_BINDTODEVICE: Final[int] = 4107
SO_BROADCAST: Final[int] = 32
AF_INET6: Final[int] = 10
IPPROTO_IP: Final[int] = 0
AF_INET: Final[int] = 2
SOCK_DGRAM: Final[int] = 2
IP_ADD_MEMBERSHIP: Final[int] = 3
IPPROTO_TCP: Final[int] = 6
IPPROTO_UDP: Final[int] = 17
IPPROTO_SEC: Incomplete
_Address: TypeAlias = tuple[str, int] | tuple[str, int, int, int] | str
Socket: TypeAlias = socket

def getaddrinfo(
    host: str,
    port: int,
    af: int = 0,
    type: int = 0,
    proto: int = 0,
    flags: int = 0,
    /,
) -> list[tuple[int, int, int, str, tuple[str, int] | tuple[str, int, int, int]]]:
    """
    Translate the host/port argument into a sequence of 5-tuples that contain all the
    necessary arguments for creating a socket connected to that service. Arguments
    *af*, *type*, and *proto* (which have the same meaning as for the `socket()` function)
    can be used to filter which kind of addresses are returned. If a parameter is not
    specified or zero, all combinations of addresses can be returned (requiring
    filtering on the user side).

    The resulting list of 5-tuples has the following structure::

       (family, type, proto, canonname, sockaddr)

    The following example shows how to connect to a given url::

       s = socket.socket()
       # This assumes that if "type" is not specified, an address for
       # SOCK_STREAM will be returned, which may be not true
       s.connect(socket.getaddrinfo('www.micropython.org', 80)[0][-1])

    Recommended use of filtering params::

       s = socket.socket()
       # Guaranteed to return an address which can be connect'ed to for
       # stream operation.
       s.connect(socket.getaddrinfo('www.micropython.org', 80, 0, SOCK_STREAM)[0][-1])

    Admonition:Difference to CPython
       :class: attention

       CPython raises a ``socket.gaierror`` exception (`OSError` subclass) in case
       of error in this function. MicroPython doesn't have ``socket.gaierror``
       and raises OSError directly. Note that error numbers of `getaddrinfo()`
       form a separate namespace and may not match error numbers from
       the :mod:`errno` module. To distinguish `getaddrinfo()` errors, they are
       represented by negative numbers, whereas standard system errors are
       positive numbers (error numbers are accessible using ``e.args[0]`` property
       from an exception object). The use of negative values is a provisional
       detail which may change in the future.
    """
    ...

class socket:
    """
    A unix like socket, for more information see module ``socket``'s description.

    The name, `Socket`, used for typing is not the same as the runtime name, `socket` (note lowercase `s`).
    The reason for this difference is that the runtime uses `socket` as both a class name and as a method name and
    this is not possible within code written entirely in Python and therefore not possible within typing code.
    """

    def recvfrom(self, bufsize: int, /) -> Tuple:
        """
        Receive data from the socket. The return value is a pair *(bytes, address)* where *bytes* is a
        bytes object representing the data received and *address* is the address of the socket sending
        the data.
        """
        ...

    def recv(self, bufsize: int, /) -> bytes:
        """
        Receive data from the socket. The return value is a bytes object representing the data
        received. The maximum amount of data to be received at once is specified by bufsize.
        """
        ...

    @overload
    def makefile(self, mode: Literal["rb", "wb", "rwb"] = "rb", buffering: int = 0, /) -> Socket:
        """
        Return a file object associated with the socket. The exact returned type depends on the arguments
        given to makefile(). The support is limited to binary modes only ('rb', 'wb', and 'rwb').
        CPython's arguments: *encoding*, *errors* and *newline* are not supported.

        Admonition:Difference to CPython
           :class: attention

           As MicroPython doesn't support buffered streams, values of *buffering*
           parameter is ignored and treated as if it was 0 (unbuffered).

        Admonition:Difference to CPython
           :class: attention

           Closing the file object returned by makefile() WILL close the
           original socket as well.
        """

    @overload
    def makefile(self, mode: str, buffering: int = 0, /) -> Socket:
        """
        Return a file object associated with the socket. The exact returned type depends on the arguments
        given to makefile(). The support is limited to binary modes only ('rb', 'wb', and 'rwb').
        CPython's arguments: *encoding*, *errors* and *newline* are not supported.

        Admonition:Difference to CPython
           :class: attention

           As MicroPython doesn't support buffered streams, values of *buffering*
           parameter is ignored and treated as if it was 0 (unbuffered).

        Admonition:Difference to CPython
           :class: attention

           Closing the file object returned by makefile() WILL close the
           original socket as well.
        """

    def listen(self, backlog: int = ..., /) -> None:
        """
        Enable a server to accept connections. If *backlog* is specified, it must be at least 0
        (if it's lower, it will be set to 0); and specifies the number of unaccepted connections
        that the system will allow before refusing new connections. If not specified, a default
        reasonable value is chosen.
        """
        ...

    def fileno(self, *args, **kwargs) -> Incomplete: ...
    def sendall(self, bytes: AnyReadableBuf, /) -> int:
        """
        Send all data to the socket. The socket must be connected to a remote socket.
        Unlike `send()`, this method will try to send all of data, by sending data
        chunk by chunk consecutively.

        The behaviour of this method on non-blocking sockets is undefined. Due to this,
        on MicroPython, it's recommended to use `write()` method instead, which
        has the same "no short writes" policy for blocking sockets, and will return
        number of bytes sent on non-blocking sockets.
        """
        ...

    def setsockopt(self, level: int, optname: int, value: AnyReadableBuf | int, /) -> None:
        """
        Set the value of the given socket option. The needed symbolic constants are defined in the
        socket module (SO_* etc.). The *value* can be an integer or a bytes-like object representing
        a buffer.
        """
        ...

    def setblocking(self, value: bool, /) -> None:
        """
        Set blocking or non-blocking mode of the socket: if flag is false, the socket is set to non-blocking,
        else to blocking mode.

        This method is a shorthand for certain `settimeout()` calls:

        * ``sock.setblocking(True)`` is equivalent to ``sock.settimeout(None)``
        * ``sock.setblocking(False)`` is equivalent to ``sock.settimeout(0)``
        """
        ...

    def sendto(self, bytes: AnyReadableBuf, address: _Address, /) -> None:
        """
        Send data to the socket. The socket should not be connected to a remote socket, since the
        destination socket is specified by *address*.
        """
        ...

    def settimeout(self, value: float | None, /) -> None:
        """
        **Note**: Not every port supports this method, see below.

        Set a timeout on blocking socket operations. The value argument can be a nonnegative floating
        point number expressing seconds, or None. If a non-zero value is given, subsequent socket operations
        will raise an `OSError` exception if the timeout period value has elapsed before the operation has
        completed. If zero is given, the socket is put in non-blocking mode. If None is given, the socket
        is put in blocking mode.

        Not every :term:`MicroPython port` supports this method. A more portable and
        generic solution is to use `select.poll` object. This allows to wait on
        multiple objects at the same time (and not just on sockets, but on generic
        `stream` objects which support polling). Example::

             # Instead of:
             s.settimeout(1.0)  # time in seconds
             s.read(10)  # may timeout

             # Use:
             poller = select.poll()
             poller.register(s, select.POLLIN)
             res = poller.poll(1000)  # time in milliseconds
             if not res:
                 # s is still not ready for input, i.e. operation timed out

        Admonition:Difference to CPython
           :class: attention

           CPython raises a ``socket.timeout`` exception in case of timeout,
           which is an `OSError` subclass. MicroPython raises an OSError directly
           instead. If you use ``except OSError:`` to catch the exception,
           your code will work both in MicroPython and CPython.
        """
        ...

    def readline(self) -> bytes:
        """
        Read a line, ending in a newline character.

        Return value: the line read.
        """
        ...

    @overload
    def readinto(self, buf: AnyWritableBuf, /) -> int | None:
        """
        Read bytes into the *buf*.  If *nbytes* is specified then read at most
        that many bytes.  Otherwise, read at most *len(buf)* bytes. Just as
        `read()`, this method follows "no short reads" policy.

        Return value: number of bytes read and stored into *buf*.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, nbytes: int, /) -> int | None:
        """
        Read bytes into the *buf*.  If *nbytes* is specified then read at most
        that many bytes.  Otherwise, read at most *len(buf)* bytes. Just as
        `read()`, this method follows "no short reads" policy.

        Return value: number of bytes read and stored into *buf*.
        """

    @overload
    def read(self) -> bytes:
        """
        Read up to size bytes from the socket. Return a bytes object. If *size* is not given, it
        reads all data available from the socket until EOF; as such the method will not return until
        the socket is closed. This function tries to read as much data as
        requested (no "short reads"). This may be not possible with
        non-blocking socket though, and then less data will be returned.
        """

    @overload
    def read(self, size: int, /) -> bytes:
        """
        Read up to size bytes from the socket. Return a bytes object. If *size* is not given, it
        reads all data available from the socket until EOF; as such the method will not return until
        the socket is closed. This function tries to read as much data as
        requested (no "short reads"). This may be not possible with
        non-blocking socket though, and then less data will be returned.
        """

    def close(self) -> None:
        """
        Mark the socket closed and release all resources. Once that happens, all future operations
        on the socket object will fail. The remote end will receive EOF indication if
        supported by protocol.

        Sockets are automatically closed when they are garbage-collected, but it is recommended
        to `close()` them explicitly as soon you finished working with them.
        """
        ...

    def connect(self, address: _Address | bytes, /) -> None:
        """
        Connect to a remote socket at *address*.
        """
        ...

    def send(self, bytes: AnyReadableBuf, /) -> int:
        """
        Send data to the socket. The socket must be connected to a remote socket.
        Returns number of bytes sent, which may be smaller than the length of data
        ("short write").
        """
        ...

    def bind(self, address: _Address | bytes, /) -> None:
        """
        Bind the socket to *address*. The socket must not already be bound.
        """
        ...

    def accept(self) -> Tuple:
        """
        Accept a connection. The socket must be bound to an address and listening for connections.
        The return value is a pair (conn, address) where conn is a new socket object usable to send
        and receive data on the connection, and address is the address bound to the socket on the
        other end of the connection.
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> int:
        """
        Write the buffer of bytes to the socket. This function will try to
        write all data to a socket (no "short writes"). This may be not possible
        with a non-blocking socket though, and returned value will be less than
        the length of *buf*.

        Return value: number of bytes written.
        """
        ...

    def __init__(
        self,
        af: int = AF_INET,
        type: int = SOCK_STREAM,
        proto: int = IPPROTO_TCP,
        /,
    ) -> None:
        """
        Create a new socket using the given address family, socket type and
        protocol number. Note that specifying *proto* in most cases is not
        required (and not recommended, as some MicroPython ports may omit
        ``IPPROTO_*`` constants). Instead, *type* argument will select needed
        protocol automatically::

                # Create STREAM TCP socket
                socket(AF_INET, SOCK_STREAM)
                # Create DGRAM UDP socket
                socket(AF_INET, SOCK_DGRAM)
        """
