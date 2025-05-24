"""
TLS/SSL wrapper for socket objects.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/ssl.html

CPython module: :mod:`python:ssl` https://docs.python.org/3/library/ssl.html .

This module provides access to Transport Layer Security (previously and
widely known as “Secure Sockets Layer”) encryption and peer authentication
facilities for network sockets, both client-side and server-side.
"""

from __future__ import annotations
import enum
import socket
import sys
from _ssl import (
    _DEFAULT_CIPHERS as _DEFAULT_CIPHERS,
    _OPENSSL_API_VERSION as _OPENSSL_API_VERSION,
    HAS_ALPN as HAS_ALPN,
    HAS_ECDH as HAS_ECDH,
    HAS_NPN as HAS_NPN,
    HAS_SNI as HAS_SNI,
    OPENSSL_VERSION as OPENSSL_VERSION,
    OPENSSL_VERSION_INFO as OPENSSL_VERSION_INFO,
    OPENSSL_VERSION_NUMBER as OPENSSL_VERSION_NUMBER,
    HAS_SSLv2 as HAS_SSLv2,
    HAS_SSLv3 as HAS_SSLv3,
    HAS_TLSv1 as HAS_TLSv1,
    HAS_TLSv1_1 as HAS_TLSv1_1,
    HAS_TLSv1_2 as HAS_TLSv1_2,
    HAS_TLSv1_3 as HAS_TLSv1_3,
    MemoryBIO as MemoryBIO,
    RAND_add as RAND_add,
    RAND_bytes as RAND_bytes,
    RAND_status as RAND_status,
    SSLSession as SSLSession,
    _PasswordType as _PasswordType,  # typeshed only, but re-export for other type stubs to use
    _SSLContext,
)
from _typeshed import Incomplete, ReadableBuffer, StrOrBytesPath, WriteableBuffer
from collections.abc import Callable, Iterable
from typing import Any, Literal, NamedTuple, TypedDict, overload
from typing_extensions import Awaitable, TypeVar, Never, Self, TypeAlias
from _mpy_shed import StrOrBytesPath
from tls import *

if sys.version_info >= (3, 13):
    from _ssl import HAS_PSK as HAS_PSK

if sys.version_info < (3, 12):
    from _ssl import RAND_pseudo_bytes as RAND_pseudo_bytes

if sys.version_info < (3, 10):
    from _ssl import RAND_egd as RAND_egd

if sys.platform == "win32":
    from _ssl import enum_certificates as enum_certificates, enum_crls as enum_crls

_PCTRTT: TypeAlias = tuple[tuple[str, str], ...]
_PCTRTTT: TypeAlias = tuple[_PCTRTT, ...]
_PeerCertRetDictType: TypeAlias = dict[str, str | _PCTRTTT | _PCTRTT]
_PeerCertRetType: TypeAlias = _PeerCertRetDictType | bytes | None
_SrvnmeCbType: TypeAlias = Callable[[SSLSocket | SSLObject, str | None, SSLSocket], int | None]

# socket_error = OSError

class _Cipher(TypedDict):
    aead: bool
    alg_bits: int
    auth: str
    description: str
    digest: str | None
    id: int
    kea: str
    name: str
    protocol: str
    strength_bits: int
    symmetric: str

class SSLError(OSError):
    library: str
    reason: str

class SSLZeroReturnError(SSLError): ...
class SSLWantReadError(SSLError): ...
class SSLWantWriteError(SSLError): ...
class SSLSyscallError(SSLError): ...
class SSLEOFError(SSLError): ...

class SSLCertVerificationError(SSLError, ValueError):
    verify_code: int
    verify_message: str

# CertificateError = SSLCertVerificationError

if sys.version_info < (3, 12):
    def wrap_socket(
        sock: socket.socket,
        *,
        server_side: bool = False,
        key: Incomplete = None,
        cert: Incomplete = None,
        cert_reqs: int = 0,
        cadata: bytes | None = None,
        server_hostname: str | None = None,
        do_handshake: bool = True,
    ) -> SSLSocket:
        """
         Wrap the given *sock* and return a new wrapped-socket object.  The implementation
         of this function is to first create an `SSLContext` and then call the `SSLContext.wrap_socket`
         method on that context object.  The arguments *sock*, *server_side* and *server_hostname* are
         passed through unchanged to the method call.  The argument *do_handshake* is passed through as
         *do_handshake_on_connect*.  The remaining arguments have the following behaviour:

        - *cert_reqs* determines whether the peer (server or client) must present a valid certificate.
          Note that for mbedtls based ports, ``ssl.CERT_NONE`` and ``ssl.CERT_OPTIONAL`` will not
          validate any certificate, only ``ssl.CERT_REQUIRED`` will.

        - *cadata* is a bytes object containing the CA certificate chain (in DER format) that will
          validate the peer's certificate.  Currently only a single DER-encoded certificate is supported.

        Depending on the underlying module implementation in a particular
        :term:`MicroPython port`, some or all keyword arguments above may be not supported.
        """
        ...

def __mpy_has_no_create_default_context(
    purpose: Purpose = ...,
    *,
    cafile: StrOrBytesPath | None = None,
    capath: StrOrBytesPath | None = None,
    cadata: str | ReadableBuffer | None = None,
) -> SSLContext: ...

if sys.version_info >= (3, 10):
    def _create_unverified_context(
        protocol: int | None = None,
        *,
        cert_reqs: int = ...,
        check_hostname: bool = False,
        purpose: Purpose = ...,
        certfile: StrOrBytesPath | None = None,
        keyfile: StrOrBytesPath | None = None,
        cafile: StrOrBytesPath | None = None,
        capath: StrOrBytesPath | None = None,
        cadata: str | ReadableBuffer | None = None,
    ) -> SSLContext: ...

else:
    def _create_unverified_context(
        protocol: int = ...,
        *,
        cert_reqs: int = ...,
        check_hostname: bool = False,
        purpose: Purpose = ...,
        certfile: StrOrBytesPath | None = None,
        keyfile: StrOrBytesPath | None = None,
        cafile: StrOrBytesPath | None = None,
        capath: StrOrBytesPath | None = None,
        cadata: str | ReadableBuffer | None = None,
    ) -> SSLContext: ...

_create_default_https_context: Callable[..., SSLContext]

if sys.version_info < (3, 12):
    def match_hostname(cert: _PeerCertRetDictType, hostname: str) -> None: ...

def cert_time_to_seconds(cert_time: str) -> int: ...

if sys.version_info >= (3, 10):
    def get_server_certificate(addr: tuple[str, int], ssl_version: int = ..., ca_certs: str | None = None, timeout: float = ...) -> str: ...

else:
    def get_server_certificate(addr: tuple[str, int], ssl_version: int = ..., ca_certs: str | None = None) -> str: ...

def DER_cert_to_PEM_cert(der_cert_bytes: ReadableBuffer) -> str: ...
def PEM_cert_to_DER_cert(pem_cert_string: str) -> bytes: ...

class DefaultVerifyPaths(NamedTuple):
    cafile: str
    capath: str
    openssl_cafile_env: str
    openssl_cafile: str
    openssl_capath_env: str
    openssl_capath: str

def get_default_verify_paths() -> DefaultVerifyPaths: ...

class VerifyMode(enum.IntEnum):
    CERT_NONE = 0
    CERT_OPTIONAL = 1
    CERT_REQUIRED = 2

CERT_NONE: VerifyMode
CERT_OPTIONAL: VerifyMode
CERT_REQUIRED: VerifyMode

class VerifyFlags(enum.IntFlag):
    VERIFY_DEFAULT = 0
    VERIFY_CRL_CHECK_LEAF = 4
    VERIFY_CRL_CHECK_CHAIN = 12
    VERIFY_X509_STRICT = 32
    VERIFY_X509_TRUSTED_FIRST = 32768
    if sys.version_info >= (3, 10):
        VERIFY_ALLOW_PROXY_CERTS = 64
        VERIFY_X509_PARTIAL_CHAIN = 524288

# VERIFY_DEFAULT: VerifyFlags
# VERIFY_CRL_CHECK_LEAF: VerifyFlags
# VERIFY_CRL_CHECK_CHAIN: VerifyFlags
# VERIFY_X509_STRICT: VerifyFlags
# VERIFY_X509_TRUSTED_FIRST: VerifyFlags

if sys.version_info >= (3, 10):
    VERIFY_ALLOW_PROXY_CERTS: VerifyFlags
    VERIFY_X509_PARTIAL_CHAIN: VerifyFlags

class _SSLMethod(enum.IntEnum):
    PROTOCOL_SSLv23 = 2
    PROTOCOL_SSLv2 = ...
    PROTOCOL_SSLv3 = ...
    PROTOCOL_TLSv1 = 3
    PROTOCOL_TLSv1_1 = 4
    PROTOCOL_TLSv1_2 = 5
    PROTOCOL_TLS = 2
    PROTOCOL_TLS_CLIENT = 16
    PROTOCOL_TLS_SERVER = 17

# PROTOCOL_SSLv23: _SSLMethod
# PROTOCOL_SSLv2: _SSLMethod
# PROTOCOL_SSLv3: _SSLMethod
# PROTOCOL_TLSv1: _SSLMethod
# PROTOCOL_TLSv1_1: _SSLMethod
# PROTOCOL_TLSv1_2: _SSLMethod
# PROTOCOL_TLS: _SSLMethod
PROTOCOL_TLS_CLIENT: _SSLMethod
PROTOCOL_TLS_SERVER: _SSLMethod

class Options(enum.IntFlag):
    OP_ALL = 2147483728
    OP_NO_SSLv2 = 0
    OP_NO_SSLv3 = 33554432
    OP_NO_TLSv1 = 67108864
    OP_NO_TLSv1_1 = 268435456
    OP_NO_TLSv1_2 = 134217728
    OP_NO_TLSv1_3 = 536870912
    OP_CIPHER_SERVER_PREFERENCE = 4194304
    OP_SINGLE_DH_USE = 0
    OP_SINGLE_ECDH_USE = 0
    OP_NO_COMPRESSION = 131072
    OP_NO_TICKET = 16384
    OP_NO_RENEGOTIATION = 1073741824
    OP_ENABLE_MIDDLEBOX_COMPAT = 1048576
    if sys.version_info >= (3, 12):
        OP_LEGACY_SERVER_CONNECT = 4
        OP_ENABLE_KTLS = 8
    if sys.version_info >= (3, 11) or sys.platform == "linux":
        OP_IGNORE_UNEXPECTED_EOF = 128

# OP_ALL: Options
# OP_NO_SSLv2: Options
# OP_NO_SSLv3: Options
# OP_NO_TLSv1: Options
# OP_NO_TLSv1_1: Options
# OP_NO_TLSv1_2: Options
# OP_NO_TLSv1_3: Options
# OP_CIPHER_SERVER_PREFERENCE: Options
# OP_SINGLE_DH_USE: Options
# OP_SINGLE_ECDH_USE: Options
# OP_NO_COMPRESSION: Options
# OP_NO_TICKET: Options
# OP_NO_RENEGOTIATION: Options
# OP_ENABLE_MIDDLEBOX_COMPAT: Options
if sys.version_info >= (3, 12):
    OP_LEGACY_SERVER_CONNECT: Options
    OP_ENABLE_KTLS: Options
if sys.version_info >= (3, 11) or sys.platform == "linux":
    OP_IGNORE_UNEXPECTED_EOF: Options

# HAS_NEVER_CHECK_COMMON_NAME: bool

# CHANNEL_BINDING_TYPES: list[str]

class AlertDescription(enum.IntEnum):
    ALERT_DESCRIPTION_ACCESS_DENIED = 49
    ALERT_DESCRIPTION_BAD_CERTIFICATE = 42
    ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE = 114
    ALERT_DESCRIPTION_BAD_CERTIFICATE_STATUS_RESPONSE = 113
    ALERT_DESCRIPTION_BAD_RECORD_MAC = 20
    ALERT_DESCRIPTION_CERTIFICATE_EXPIRED = 45
    ALERT_DESCRIPTION_CERTIFICATE_REVOKED = 44
    ALERT_DESCRIPTION_CERTIFICATE_UNKNOWN = 46
    ALERT_DESCRIPTION_CERTIFICATE_UNOBTAINABLE = 111
    ALERT_DESCRIPTION_CLOSE_NOTIFY = 0
    ALERT_DESCRIPTION_DECODE_ERROR = 50
    ALERT_DESCRIPTION_DECOMPRESSION_FAILURE = 30
    ALERT_DESCRIPTION_DECRYPT_ERROR = 51
    ALERT_DESCRIPTION_HANDSHAKE_FAILURE = 40
    ALERT_DESCRIPTION_ILLEGAL_PARAMETER = 47
    ALERT_DESCRIPTION_INSUFFICIENT_SECURITY = 71
    ALERT_DESCRIPTION_INTERNAL_ERROR = 80
    ALERT_DESCRIPTION_NO_RENEGOTIATION = 100
    ALERT_DESCRIPTION_PROTOCOL_VERSION = 70
    ALERT_DESCRIPTION_RECORD_OVERFLOW = 22
    ALERT_DESCRIPTION_UNEXPECTED_MESSAGE = 10
    ALERT_DESCRIPTION_UNKNOWN_CA = 48
    ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY = 115
    ALERT_DESCRIPTION_UNRECOGNIZED_NAME = 112
    ALERT_DESCRIPTION_UNSUPPORTED_CERTIFICATE = 43
    ALERT_DESCRIPTION_UNSUPPORTED_EXTENSION = 110
    ALERT_DESCRIPTION_USER_CANCELLED = 90

# ALERT_DESCRIPTION_HANDSHAKE_FAILURE: AlertDescription
# ALERT_DESCRIPTION_INTERNAL_ERROR: AlertDescription
# ALERT_DESCRIPTION_ACCESS_DENIED: AlertDescription
# ALERT_DESCRIPTION_BAD_CERTIFICATE: AlertDescription
# ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE: AlertDescription
# ALERT_DESCRIPTION_BAD_CERTIFICATE_STATUS_RESPONSE: AlertDescription
# ALERT_DESCRIPTION_BAD_RECORD_MAC: AlertDescription
# ALERT_DESCRIPTION_CERTIFICATE_EXPIRED: AlertDescription
# ALERT_DESCRIPTION_CERTIFICATE_REVOKED: AlertDescription
# ALERT_DESCRIPTION_CERTIFICATE_UNKNOWN: AlertDescription
# ALERT_DESCRIPTION_CERTIFICATE_UNOBTAINABLE: AlertDescription
# ALERT_DESCRIPTION_CLOSE_NOTIFY: AlertDescription
# ALERT_DESCRIPTION_DECODE_ERROR: AlertDescription
# ALERT_DESCRIPTION_DECOMPRESSION_FAILURE: AlertDescription
# ALERT_DESCRIPTION_DECRYPT_ERROR: AlertDescription
# ALERT_DESCRIPTION_ILLEGAL_PARAMETER: AlertDescription
# ALERT_DESCRIPTION_INSUFFICIENT_SECURITY: AlertDescription
# ALERT_DESCRIPTION_NO_RENEGOTIATION: AlertDescription
# ALERT_DESCRIPTION_PROTOCOL_VERSION: AlertDescription
# ALERT_DESCRIPTION_RECORD_OVERFLOW: AlertDescription
# ALERT_DESCRIPTION_UNEXPECTED_MESSAGE: AlertDescription
# ALERT_DESCRIPTION_UNKNOWN_CA: AlertDescription
# ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY: AlertDescription
# ALERT_DESCRIPTION_UNRECOGNIZED_NAME: AlertDescription
# ALERT_DESCRIPTION_UNSUPPORTED_CERTIFICATE: AlertDescription
# ALERT_DESCRIPTION_UNSUPPORTED_EXTENSION: AlertDescription
# ALERT_DESCRIPTION_USER_CANCELLED: AlertDescription

class _ASN1ObjectBase(NamedTuple):
    nid: int
    shortname: str
    longname: str
    oid: str

class _ASN1Object(_ASN1ObjectBase):
    def __new__(cls, oid: str) -> Self: ...
    @classmethod
    def fromnid(cls, nid: int) -> Self: ...
    @classmethod
    def fromname(cls, name: str) -> Self: ...

class Purpose(_ASN1Object, enum.Enum):
    SERVER_AUTH = (129, "serverAuth", "TLS Web Server Authentication", "1.3.6.1.5.5.7.3.2")  # pyright: ignore[reportCallIssue]
    CLIENT_AUTH = (130, "clientAuth", "TLS Web Client Authentication", "1.3.6.1.5.5.7.3.1")  # pyright: ignore[reportCallIssue]

class SSLSocket:
    context: SSLContext
    server_side: bool
    server_hostname: str | None
    session: SSLSession | None
    @property
    def session_reused(self) -> bool | None: ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def connect(self, addr: socket._Address) -> None: ...
    def connect_ex(self, addr: socket._Address) -> int: ...
    # ifdef MBEDTLS_SSL_PROTO_DTLS
    @overload  # force merge
    def recv(self, *argv, **kwargs) -> Incomplete: ...
    @overload  # force merge
    def recv_into(self, *argv, **kwargs) -> Incomplete: ...
    def recvfrom(self, buflen: int = 1024, flags: int = 0) -> tuple[bytes, socket._RetAddress]: ...
    def recvfrom_into(self, buffer: WriteableBuffer, nbytes: int | None = None, flags: int = 0) -> tuple[int, socket._RetAddress]: ...
    @overload  # force merge
    def send(self, *argv, **kwargs) -> Incomplete: ...
    @overload  # force merge
    def sendall(self, *argv, **kwargs) -> Incomplete: ...
    @overload
    def sendto(self, data: ReadableBuffer, flags_or_addr: socket._Address, addr: None = None) -> int: ...
    @overload
    def sendto(self, data: ReadableBuffer, flags_or_addr: int, addr: socket._Address) -> int: ...
    def shutdown(self, how: int) -> None: ...
    # TODO : SSLSocket is undocumented
    # ref: micropython\extmod\modtls_axtls.c ( read ... close)

    # repos\micropython\extmod\modtls_mbedtls.c
    @overload  # force merge
    def read(self, *argv, **kwargs) -> Incomplete: ...
    @overload  # force merge
    def write(self, *argv, **kwargs) -> Incomplete: ...
    def do_handshake(self, block: bool = False) -> None: ...  # block is undocumented
    @overload
    def getpeercert(self, binary_form: Literal[False] = False) -> _PeerCertRetDictType | None: ...
    @overload
    def getpeercert(self, binary_form: Literal[True]) -> bytes | None: ...
    @overload
    def getpeercert(self, binary_form: bool) -> _PeerCertRetType: ...
    # endif
    # ifdef (MBEDTLS_SSL_KEEP_PEER_CERTIFICATE)
    @overload  # force merge
    def getpeercert(self, *argv, **kwargs) -> Incomplete: ...
    # endif
    @overload  # force merge
    def cipher(self, *argv, **kwargs) -> Incomplete: ...
    def shared_ciphers(self) -> list[tuple[str, str, int]] | None: ...
    def compression(self) -> str | None: ...
    def get_channel_binding(self, cb_type: str = "tls-unique") -> bytes | None: ...
    def selected_alpn_protocol(self) -> str | None: ...
    def selected_npn_protocol(self) -> str | None: ...
    def accept(self) -> tuple[SSLSocket, socket._RetAddress]: ...
    def unwrap(self) -> socket.socket: ...
    def version(self) -> str | None: ...
    def pending(self) -> int: ...
    def verify_client_post_handshake(self) -> None: ...
    # These methods always raise `NotImplementedError`:
    def recvmsg(self, *args: Never, **kwargs: Never) -> Never: ...  # type: ignore[override]
    def recvmsg_into(self, *args: Never, **kwargs: Never) -> Never: ...  # type: ignore[override]
    def sendmsg(self, *args: Never, **kwargs: Never) -> Never: ...  # type: ignore[override]
    if sys.version_info >= (3, 13):
        def get_verified_chain(self) -> list[bytes]: ...
        def get_unverified_chain(self) -> list[bytes]: ...

    @overload  # force merge
    def readinto(self, *argv, **kwargs) -> Incomplete: ...
    @overload  # force merge
    def readline(self, *argv, **kwargs) -> Incomplete: ...
    @overload  # force merge
    def setblocking(self, *argv, **kwargs) -> Incomplete: ...
    @overload  # force merge
    def close(self, *argv, **kwargs) -> Incomplete: ...
    # if MICROPY_PY_SSL_FINALISER
    @overload  # force merge
    def __del__(self, *argv, **kwargs) -> Incomplete: ...
    # endif
    # ifdef MICROPY_UNIX_COVERAGE
    @overload  # force merge
    def ioctl(self, *argv, **kwargs) -> Incomplete: ...

class TLSVersion(enum.IntEnum):
    MINIMUM_SUPPORTED = -2
    MAXIMUM_SUPPORTED = -1
    SSLv3 = 768
    TLSv1 = 769
    TLSv1_1 = 770
    TLSv1_2 = 771
    TLSv1_3 = 772

class SSLContext:
    """
    Create a new SSLContext instance.  The *protocol* argument must be one of the ``PROTOCOL_*``
    constants.
    """

    options: Options
    verify_flags: VerifyFlags
    verify_mode: VerifyMode
    @property
    def protocol(self) -> _SSLMethod: ...  # type: ignore[override]
    hostname_checks_common_name: bool
    maximum_version: TLSVersion
    minimum_version: TLSVersion
    # The following two attributes have class-level defaults.
    # However, the docs explicitly state that it's OK to override these attributes on instances,
    # so making these ClassVars wouldn't be appropriate
    sslobject_class: type[SSLObject]
    sslsocket_class: type[SSLSocket]
    keylog_filename: str
    post_handshake_auth: bool
    if sys.version_info >= (3, 10):
        security_level: int
    if sys.version_info >= (3, 10):
        # Using the default (None) for the `protocol` parameter is deprecated,
        # but there isn't a good way of marking that in the stub unless/until PEP 702 is accepted
        def __new__(cls, protocol: int | None = None, *args: Any, **kwargs: Any) -> Self: ...
    else:
        def __new__(cls, protocol: int = ..., *args: Any, **kwargs: Any) -> Self: ...

    def load_default_certs(self, purpose: Purpose = ...) -> None: ...
    def load_verify_locations(self, cafile=None, cadata: bytes | None = None) -> None:
        """
        Load the CA certificate chain that will validate the peer's certificate.
        *cafile* is the file path of the CA certificates.  *cadata* is a bytes object
        containing the CA certificates.  Only one of these arguments should be provided.
        """
        ...

    @overload
    def get_ca_certs(self, binary_form: Literal[False] = False) -> list[_PeerCertRetDictType]: ...
    @overload
    def get_ca_certs(self, binary_form: Literal[True]) -> list[bytes]: ...
    @overload
    def get_ca_certs(self, binary_form: bool = False) -> Any: ...
    def get_ciphers(self) -> list[_Cipher]:
        """
        Get a list of enabled ciphers, returned as a list of strings.
        """
        ...

    def set_default_verify_paths(self) -> None: ...
    def set_ciphers(self, ciphers) -> None:
        """
        Set the available ciphers for sockets created with this context.  *ciphers* should be
        a list of strings in the `IANA cipher suite format <https://wiki.mozilla.org/Security/Cipher_Suites>`_ .
        """
        ...

    def set_alpn_protocols(self, alpn_protocols: Iterable[str]) -> None: ...
    def set_npn_protocols(self, npn_protocols: Iterable[str]) -> None: ...
    def set_servername_callback(self, server_name_callback: _SrvnmeCbType | None) -> None: ...
    def load_dh_params(self, path: str, /) -> None: ...
    def set_ecdh_curve(self, name: str, /) -> None: ...
    def wrap_socket(
        self,
        sock: socket,
        *,
        server_side: bool = False,
        do_handshake_on_connect: bool = True,
        server_hostname: str | None = None,
    ) -> SSLSocket:
        """
        Takes a `stream` *sock* (usually socket.socket instance of ``SOCK_STREAM`` type),
        and returns an instance of ssl.SSLSocket, wrapping the underlying stream.
        The returned object has the usual `stream` interface methods like
        ``read()``, ``write()``, etc.

        - *server_side* selects whether the wrapped socket is on the server or client side.
          A server-side SSL socket should be created from a normal socket returned from
          :meth:`~socket.socket.accept()` on a non-SSL listening server socket.

        - *do_handshake_on_connect* determines whether the handshake is done as part of the ``wrap_socket``
          or whether it is deferred to be done as part of the initial reads or writes
          For blocking sockets doing the handshake immediately is standard. For non-blocking
          sockets (i.e. when the *sock* passed into ``wrap_socket`` is in non-blocking mode)
          the handshake should generally be deferred because otherwise ``wrap_socket`` blocks
          until it completes. Note that in AXTLS the handshake can be deferred until the first
          read or write but it then blocks until completion.

        - *server_hostname* is for use as a client, and sets the hostname to check against the received
          server certificate.  It also sets the name for Server Name Indication (SNI), allowing the server
          to present the proper certificate.
        """
        ...

    def wrap_bio(
        self,
        incoming: MemoryBIO,
        outgoing: MemoryBIO,
        server_side: bool = False,
        server_hostname: str | bytes | None = None,
        session: SSLSession | None = None,
    ) -> SSLObject: ...
    @overload  # force merge
    def load_cert_chain(self, certfile, keyfile) -> None:
        """
        Load a private key and the corresponding certificate.  The *certfile* is a string
        with the file path of the certificate.  The *keyfile* is a string with the file path
        of the private key.

        Admonition:Difference to CPython
           :class: attention

           MicroPython extension: *certfile* and *keyfile* can be bytes objects instead of
           strings, in which case they are interpreted as the actual certificate/key data.
        """
        ...

    @overload  # force merge
    def load_cert_chain(self, certfile, keyfile) -> None:
        """
        Load a private key and the corresponding certificate.  The *certfile* is a string
        with the file path of the certificate.  The *keyfile* is a string with the file path
        of the private key.

        Admonition:Difference to CPython
           :class: attention

           MicroPython extension: *certfile* and *keyfile* can be bytes objects instead of
           strings, in which case they are interpreted as the actual certificate/key data.
        """
        ...

class SSLObject:
    context: SSLContext
    @property
    def server_side(self) -> bool: ...
    @property
    def server_hostname(self) -> str | None: ...
    session: SSLSession | None
    @property
    def session_reused(self) -> bool: ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def read(self, len: int = 1024, buffer: bytearray | None = None) -> bytes: ...
    def write(self, data: ReadableBuffer) -> int: ...
    @overload
    def getpeercert(self, binary_form: Literal[False] = False) -> _PeerCertRetDictType | None: ...
    @overload
    def getpeercert(self, binary_form: Literal[True]) -> bytes | None: ...
    @overload
    def getpeercert(self, binary_form: bool) -> _PeerCertRetType: ...
    def selected_alpn_protocol(self) -> str | None: ...
    def selected_npn_protocol(self) -> str | None: ...
    def cipher(self) -> tuple[str, str, int] | None: ...
    def shared_ciphers(self) -> list[tuple[str, str, int]] | None: ...
    def compression(self) -> str | None: ...
    def pending(self) -> int: ...
    def do_handshake(self) -> None: ...
    def unwrap(self) -> None: ...
    def version(self) -> str | None: ...
    def get_channel_binding(self, cb_type: str = "tls-unique") -> bytes | None: ...
    def verify_client_post_handshake(self) -> None: ...
    if sys.version_info >= (3, 13):
        def get_verified_chain(self) -> list[bytes]: ...
        def get_unverified_chain(self) -> list[bytes]: ...

class SSLErrorNumber(enum.IntEnum):
    SSL_ERROR_EOF = 8
    SSL_ERROR_INVALID_ERROR_CODE = 10
    SSL_ERROR_SSL = 1
    SSL_ERROR_SYSCALL = 5
    SSL_ERROR_WANT_CONNECT = 7
    SSL_ERROR_WANT_READ = 2
    SSL_ERROR_WANT_WRITE = 3
    SSL_ERROR_WANT_X509_LOOKUP = 4
    SSL_ERROR_ZERO_RETURN = 6

# SSL_ERROR_EOF: SSLErrorNumber  # undocumented
# SSL_ERROR_INVALID_ERROR_CODE: SSLErrorNumber  # undocumented
# SSL_ERROR_SSL: SSLErrorNumber  # undocumented
# SSL_ERROR_SYSCALL: SSLErrorNumber  # undocumented
# SSL_ERROR_WANT_CONNECT: SSLErrorNumber  # undocumented
# SSL_ERROR_WANT_READ: SSLErrorNumber  # undocumented
# SSL_ERROR_WANT_WRITE: SSLErrorNumber  # undocumented
# SSL_ERROR_WANT_X509_LOOKUP: SSLErrorNumber  # undocumented
# SSL_ERROR_ZERO_RETURN: SSLErrorNumber  # undocumented

def get_protocol_name(protocol_code: int) -> str: ...

if sys.version_info < (3, 9):
    AF_INET: int
# PEM_FOOTER: str
# PEM_HEADER: str
# SOCK_STREAM: int
# SOL_SOCKET: int
# SO_TYPE: int
MBEDTLS_VERSION: str = "Mbed TLS 3.6.0"
