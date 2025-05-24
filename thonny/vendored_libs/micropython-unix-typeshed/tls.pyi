"""
Module: 'tls' on micropython-v1.24.1-unix
"""

# MCU: {'family': 'micropython', 'version': '1.24.1', 'build': '', 'ver': '1.24.1', 'port': 'unix', 'board': '', 'cpu': 'linux [GCC 12.4.0] version', 'mpy': 'v6.3', 'arch': 'x64'}
# Stubber: v1.24.0
from __future__ import annotations
from typing import Any, Final, Generator
from _typeshed import Incomplete

MBEDTLS_VERSION: Final[str] = "Mbed TLS 3.5.1"
PROTOCOL_TLS_SERVER: Final[int] = 1
PROTOCOL_TLS_CLIENT: Final[int] = 0
CERT_NONE: Final[int] = 0
CERT_REQUIRED: Final[int] = 2
CERT_OPTIONAL: Final[int] = 1

class SSLContext:
    def load_verify_locations(self, *args, **kwargs) -> Incomplete: ...
    def set_ciphers(self, *args, **kwargs) -> Incomplete: ...
    def wrap_socket(self, *args, **kwargs) -> Incomplete: ...
    def load_cert_chain(self, *args, **kwargs) -> Incomplete: ...
    def get_ciphers(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...
