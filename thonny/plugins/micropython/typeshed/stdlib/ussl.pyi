"""
TLS/SSL wrapper for socket objects.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/ssl.rst.

|see_cpython_module| :mod:`python:ssl`.

This module provides access to Transport Layer Security (previously and
widely known as “Secure Sockets Layer”) encryption and peer authentication
facilities for network sockets, both client-side and server-side.

.. admonition:: Difference to CPython
   :class: attention
The CPython version of ``ssl`` uses ``SSLError``.
      This exception does NOT exist. Instead its base class, OSError, is used.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final

from uio import StrOrBytesPath
from usocket import Socket

def wrap_socket(
    sock: Socket,
    server_side: bool = False,
    keyfile: StrOrBytesPath | None = None,
    certfile: StrOrBytesPath | None = None,
    cert_reqs: int = "CERT_NONE",
    ca_certs: str | None = None,
    do_handshake: bool = True,
    /,
) -> Socket:
    """
   Takes a `stream` *sock* (usually socket.socket instance of ``SOCK_STREAM`` type),
   and returns an instance of ssl.SSLSocket, which wraps the underlying stream in
   an SSL context. Returned object has the usual `stream` interface methods like
   ``read()``, ``write()``, etc.
   A server-side SSL socket should be created from a normal socket returned from
   :meth:`~socket.socket.accept()` on a non-SSL listening server socket.
   
   - *do_handshake* determines whether the handshake is done as part of the ``wrap_socket``
     or whether it is deferred to be done as part of the initial reads or writes
     (there is no ``do_handshake`` method as in CPython).
     For blocking sockets doing the handshake immediately is standard. For non-blocking
     sockets (i.e. when the *sock* passed into ``wrap_socket`` is in non-blocking mode)
     the handshake should generally be deferred because otherwise ``wrap_socket`` blocks
     until it completes. Note that in AXTLS the handshake can be deferred until the first
     read or write but it then blocks until completion.
   
   Depending on the underlying module implementation in a particular
   :term:`MicroPython port`, some or all keyword arguments above may be not supported.
   """

CERT_NONE: Final[int] = ...
"""
Supported values for *cert_reqs* parameter.
"""

CERT_OPTIONAL: Final[int] = ...
"""
Supported values for *cert_reqs* parameter.
"""

CERT_REQUIRED: Final[int] = ...
"""
Supported values for *cert_reqs* parameter.
"""
