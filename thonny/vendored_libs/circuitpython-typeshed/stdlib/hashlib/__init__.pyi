"""Hashing related functions

|see_cpython_module| :mod:`cpython:hashlib`.
"""

from __future__ import annotations

import hashlib

from circuitpython_typing import ReadableBuffer

def new(name: str, data: bytes = b"") -> hashlib.Hash:
    """Returns a Hash object setup for the named algorithm. Raises ValueError when the named
       algorithm is unsupported.

    :return: a hash object for the given algorithm
    :rtype: hashlib.Hash"""
    ...

class Hash:
    """In progress hash algorithm. This object is always created by a `hashlib.new()`. It has no
    user-visible constructor."""

    digest_size: int
    """Digest size in bytes"""

    def update(self, data: ReadableBuffer) -> None:
        """Update the hash with the given bytes.

        :param ~circuitpython_typing.ReadableBuffer data: Update the hash from data in this buffer
        """
        ...

    def digest(self) -> bytes:
        """Returns the current digest as bytes() with a length of `hashlib.Hash.digest_size`."""
        ...
