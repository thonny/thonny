"""AES encryption routines

The `AES` module contains classes used to implement encryption
and decryption. It aims to be low overhead in terms of memory."""
class AES:
    """Encrypt and decrypt AES streams"""

    def __init__(self, key, mode=0, iv=None, segment_size=8) -> Any:
        """Create a new AES state with the given key.

           :param bytearray key: A 16-, 24-, or 32-byte key
           :param int mode: AES mode to use.  One of: AES.MODE_ECB, AES.MODE_CBC, or
                            AES.MODE_CTR
           :param bytearray iv: Initialization vector to use for CBC or CTR mode

           Additional arguments are supported for legacy reasons.

           Encrypting a string::

             import aesio
             from binascii import hexlify

             key = b'Sixteen byte key'
             inp = b'Circuit Python!!' # Note: 16-bytes long
             outp = bytearray(len(inp))
             cipher = aesio.AES(key, aesio.mode.MODE_ECB)
             cipher.encrypt_into(inp, outp)
             hexlify(outp)"""
        ...

    def encrypt_into(src, dest) -> None:
        """Encrypt the buffer from ``src`` into ``dest``.

           For ECB mode, the buffers must be 16 bytes long.  For CBC mode, the
           buffers must be a multiple of 16 bytes, and must be equal length.  For
           CTX mode, there are no restrictions."""
        ...

    def decrypt_into(src, dest) -> None:

        """Decrypt the buffer from ``src`` into ``dest``.
           For ECB mode, the buffers must be 16 bytes long.  For CBC mode, the
           buffers must be a multiple of 16 bytes, and must be equal length.  For
           CTX mode, there are no restrictions."""
        ...

