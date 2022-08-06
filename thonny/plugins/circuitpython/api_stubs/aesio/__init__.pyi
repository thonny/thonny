"""AES encryption routines

The `AES` module contains classes used to implement encryption
and decryption. It aims to be low overhead in terms of memory."""

from __future__ import annotations

from typing import Optional

from circuitpython_typing import ReadableBuffer, WriteableBuffer

MODE_ECB: int
MODE_CBC: int
MODE_CTR: int

class AES:
    """Encrypt and decrypt AES streams"""

    def __init__(
        self,
        key: ReadableBuffer,
        mode: int = 0,
        iv: Optional[ReadableBuffer] = None,
        segment_size: int = 8,
    ) -> None:
        """Create a new AES state with the given key.

        :param ~circuitpython_typing.ReadableBuffer key: A 16-, 24-, or 32-byte key
        :param int mode: AES mode to use.  One of: `MODE_ECB`, `MODE_CBC`, or
                         `MODE_CTR`
        :param ~circuitpython_typing.ReadableBuffer iv: Initialization vector to use for CBC or CTR mode

        Additional arguments are supported for legacy reasons.

        Encrypting a string::

          import aesio
          from binascii import hexlify

          key = b'Sixteen byte key'
          inp = b'CircuitPython!!!' # Note: 16-bytes long
          outp = bytearray(len(inp))
          cipher = aesio.AES(key, aesio.MODE_ECB)
          cipher.encrypt_into(inp, outp)
          hexlify(outp)"""
        ...
    def encrypt_into(self, src: ReadableBuffer, dest: WriteableBuffer) -> None:
        """Encrypt the buffer from ``src`` into ``dest``.

        For ECB mode, the buffers must be 16 bytes long.  For CBC mode, the
        buffers must be a multiple of 16 bytes, and must be equal length.  For
        CTX mode, there are no restrictions."""
        ...
    def decrypt_into(self, src: ReadableBuffer, dest: WriteableBuffer) -> None:
        """Decrypt the buffer from ``src`` into ``dest``.
        For ECB mode, the buffers must be 16 bytes long.  For CBC mode, the
        buffers must be a multiple of 16 bytes, and must be equal length.  For
        CTX mode, there are no restrictions."""
        ...
