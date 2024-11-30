import sys
from _blake2 import blake2b as blake2b, blake2s as blake2s
from _typeshed import ReadableBuffer
from collections.abc import Callable, Set as AbstractSet
from typing import Protocol
from typing_extensions import Self

if sys.version_info >= (3, 11):
    __all__ = (
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "blake2b",
        "blake2s",
        "sha3_224",
        "sha3_256",
        "sha3_384",
        "sha3_512",
        "shake_128",
        "shake_256",
        "new",
        "algorithms_guaranteed",
        "algorithms_available",
        "pbkdf2_hmac",
        "file_digest",
    )
else:
    __all__ = (
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "blake2b",
        "blake2s",
        "sha3_224",
        "sha3_256",
        "sha3_384",
        "sha3_512",
        "shake_128",
        "shake_256",
        "new",
        "algorithms_guaranteed",
        "algorithms_available",
        "pbkdf2_hmac",
    )

class _Hash:
    @property
    def digest_size(self) -> int: ...
    @property
    def block_size(self) -> int: ...
    @property
    def name(self) -> str: ...
    def copy(self) -> Self: ...
    def digest(self) -> bytes: ...
    def hexdigest(self) -> str: ...
    def update(self, data: ReadableBuffer, /) -> None: ...

class _VarLenHash:
    digest_size: int
    block_size: int
    name: str
    def copy(self) -> _VarLenHash: ...
    def digest(self, length: int, /) -> bytes: ...
    def hexdigest(self, length: int, /) -> str: ...
    def update(self, data: ReadableBuffer, /) -> None: ...

if sys.version_info >= (3, 9):
    def new(name: str, data: ReadableBuffer = b"", *, usedforsecurity: bool = ...) -> _Hash: ...
    def md5(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a md5 hash object; optionally initialized with a string"""
        ...
    def sha1(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha1 hash object; optionally initialized with a string"""
        ...
    def sha224(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha224 hash object; optionally initialized with a string"""
        ...
    def sha256(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha256 hash object; optionally initialized with a string"""
        ...
    def sha384(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha384 hash object; optionally initialized with a string"""
        ...
    def sha512(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha512 hash object; optionally initialized with a string"""
        ...
    def sha3_224(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha3-224 hash object; optionally initialized with a string"""
        ...
    def sha3_256(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha3-256 hash object; optionally initialized with a string"""
        ...
    def sha3_384(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha3-384 hash object; optionally initialized with a string"""
        ...
    def sha3_512(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _Hash:
        """Returns a sha3-512 hash object; optionally initialized with a string"""
        ...
    def shake_128(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _VarLenHash:
        """Returns a shake-128 variable hash object; optionally initialized with a string"""
        ...
    def shake_256(string: ReadableBuffer = b"", *, usedforsecurity: bool = True) -> _VarLenHash:
        """Returns a shake-256 variable hash object; optionally initialized with a string"""
        ...

else:
    def new(name: str, data: ReadableBuffer = b"") -> _Hash: ...
    def md5(string: ReadableBuffer = b"") -> _Hash:
        """Returns a md5 hash object; optionally initialized with a string"""
        ...
    def sha1(string: ReadableBuffer = b"") -> _Hash:
        """Returns a sha1 hash object; optionally initialized with a string"""
        ...
    def sha224(string: ReadableBuffer = b"") -> _Hash:
        """Returns a sha224 hash object; optionally initialized with a string"""
        ...
    def sha256(string: ReadableBuffer = b"") -> _Hash:
        """Returns a sha256 hash object; optionally initialized with a string"""
        ...
    def sha384(string: ReadableBuffer = b"") -> _Hash:
        """Returns a sha384 hash object; optionally initialized with a string"""
        ...
    def sha512(string: ReadableBuffer = b"") -> _Hash:
        """Returns a sha512 hash object; optionally initialized with a string"""
        ...
    def sha3_224(string: ReadableBuffer = b"") -> _Hash: ...
    def sha3_256(string: ReadableBuffer = b"") -> _Hash: ...
    def sha3_384(string: ReadableBuffer = b"") -> _Hash: ...
    def sha3_512(string: ReadableBuffer = b"") -> _Hash: ...
    def shake_128(string: ReadableBuffer = b"") -> _VarLenHash: ...
    def shake_256(string: ReadableBuffer = b"") -> _VarLenHash: ...

algorithms_guaranteed: AbstractSet[str]
algorithms_available: AbstractSet[str]

def pbkdf2_hmac(
    hash_name: str, password: ReadableBuffer, salt: ReadableBuffer, iterations: int, dklen: int | None = None
) -> bytes:
    """Password based key derivation function 2 (PKCS #5 v2.0) with HMAC as pseudorandom function."""
    ...
def scrypt(
    password: ReadableBuffer, *, salt: ReadableBuffer, n: int, r: int, p: int, maxmem: int = 0, dklen: int = 64
) -> bytes:
    """scrypt password-based key derivation function."""
    ...

if sys.version_info >= (3, 11):
    class _BytesIOLike(Protocol):
        def getbuffer(self) -> ReadableBuffer: ...

    class _FileDigestFileObj(Protocol):
        def readinto(self, buf: bytearray, /) -> int: ...
        def readable(self) -> bool: ...

    def file_digest(
        fileobj: _BytesIOLike | _FileDigestFileObj, digest: str | Callable[[], _Hash], /, *, _bufsize: int = 262144
    ) -> _Hash: ...
