"""Non-volatile memory

The `nvm` module allows you to store whatever raw bytes you wish in a
reserved section non-volatile memory.

Note that this module can't be imported and used directly. The sole
instance of :class:`ByteArray` is available at
:attr:`microcontroller.nvm`."""

class ByteArray:
    """Presents a stretch of non-volatile memory as a bytearray.

    Non-volatile memory is available as a byte array that persists over reloads
    and power cycles. Each assignment causes an erase and write cycle so its recommended to assign
    all values to change at once.

    Usage::

       import microcontroller
       microcontroller.nvm[0:3] = b\"\xcc\x10\x00\""""

    def __init__(self, ):
        """Not currently dynamically supported. Access the sole instance through `microcontroller.nvm`."""
        ...

    def __len__(self, ) -> Any:
        """Return the length. This is used by (`len`)"""
        ...

