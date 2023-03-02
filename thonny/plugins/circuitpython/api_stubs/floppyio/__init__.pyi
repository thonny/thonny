from __future__ import annotations

import digitalio
from circuitpython_typing import WriteableBuffer

def flux_readinto(
    buffer: WriteableBuffer, data: digitalio.DigitalInOut, index: digitalio.DigitalInOut
) -> int:
    """Read flux transition information into the buffer.

    The function returns when the buffer has filled, or when the index input
    indicates that one full revolution of data has been recorded.  Due to
    technical limitations, this process may not be interruptible by
    KeyboardInterrupt.

    :param buffer: Read data into this buffer.  Each element represents the time between successive zero-to-one transitions.
    :param data: Pin on which the flux data appears
    :param index: Pin on which the index pulse appears
    :return: The actual number of bytes of read
    """
    ...

def mfm_readinto(
    buffer: WriteableBuffer, data: digitalio.DigitalInOut, index: digitalio.DigitalInOut
) -> int:
    """Read mfm blocks into the buffer.

    The track is assumed to consist of 512-byte sectors.

    The function returns when all sectors have been successfully read, or
    a number of index pulses have occurred.  Due to technical limitations, this
    process may not be interruptible by KeyboardInterrupt.

    :param buffer: Read data into this buffer.  Must be a multiple of 512.
    :param data: Pin on which the mfm data appears
    :param index: Pin on which the index pulse appears
    :return: The actual number of sectors read
    """
    ...

samplerate: int
"""The approximate sample rate in Hz used by flux_readinto."""
