"""TCP, UDP and RAW socket support

Create TCP, UDP and RAW sockets for communicating over the Internet."""

class socket:

    def __init__(self, family: int, type: int, proto: int):
        """Create a new socket

        :param ~int family: AF_INET or AF_INET6
        :param ~int type: SOCK_STREAM, SOCK_DGRAM or SOCK_RAW
        :param ~int proto: IPPROTO_TCP, IPPROTO_UDP or IPPROTO_RAW (ignored)"""
        ...

    def bind(self, address: tuple) -> Any:
        """Bind a socket to an address

        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def listen(self, backlog: int) -> Any:
        """Set socket to listen for incoming connections

        :param ~int backlog: length of backlog queue for waiting connetions"""
        ...

    def accept(self, ) -> Any:
        """Accept a connection on a listening socket of type SOCK_STREAM,
        creating a new socket of type SOCK_STREAM.
        Returns a tuple of (new_socket, remote_address)"""

    def connect(self, address: tuple) -> Any:
        """Connect a socket to a remote address

        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def send(self, bytes: bytes) -> Any:
        """Send some bytes to the connected remote address.
        Suits sockets of type SOCK_STREAM

        :param ~bytes bytes: some bytes to send"""
        ...

    def recv_into(self, buffer: bytearray, bufsize: int) -> Any:
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

    def recv(self, bufsize: int) -> Any:
        """Reads some bytes from the connected remote address.
        Suits sockets of type SOCK_STREAM
        Returns a bytes() of length <= bufsize

        :param ~int bufsize: maximum number of bytes to receive"""
        ...

    def sendto(self, bytes: bytes, address: tuple) -> Any:
        """Send some bytes to a specific address.
        Suits sockets of type SOCK_DGRAM

        :param ~bytes bytes: some bytes to send
        :param ~tuple address: tuple of (remote_address, remote_port)"""
        ...

    def recvfrom(self, bufsize: int) -> Any:
        """Reads some bytes from the connected remote address.
        Suits sockets of type SOCK_STREAM

        Returns a tuple containing
        * a bytes() of length <= bufsize
        * a remote_address, which is a tuple of ip address and port number

        :param ~int bufsize: maximum number of bytes to receive"""
        ...

    def setsockopt(self, level: Any, optname: Any, value: Any) -> Any:
        """Sets socket options"""
        ...

    def settimeout(self, value: int) -> Any:
        """Set the timeout value for this socket.

        :param ~int value: timeout in seconds.  0 means non-blocking.  None means block indefinitely."""
        ...

    def setblocking(self, flag: bool) -> Any:
        """Set the blocking behaviour of this socket.

        :param ~bool flag: False means non-blocking, True means block indefinitely."""
        ...

def getaddrinfo(host: Any, port: Any) -> Any:
    """Gets the address information for a hostname and port

    Returns the appropriate family, socket type, socket protocol and
    address information to call socket.socket() and socket.connect() with,
    as a tuple."""
    ...

