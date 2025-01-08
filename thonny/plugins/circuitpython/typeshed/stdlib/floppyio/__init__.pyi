from __future__ import annotations

import digitalio
from circuitpython_typing import ReadableBuffer, WriteableBuffer

def flux_readinto(
    buffer: WriteableBuffer,
    data: digitalio.DigitalInOut,
    index: digitalio.DigitalInOut,
    index_wait: float = 0.220,
) -> int:
    """Read flux transition information into the buffer.

    The function returns when the buffer has filled, or when the index input
    indicates that one full revolution of data has been recorded.  Due to
    technical limitations, this process may not be interruptible by
    KeyboardInterrupt.

    :param buffer: Read data into this buffer.  Each element represents the time between successive zero-to-one transitions.
    :param data: Pin on which the flux data appears
    :param index: Pin on which the index pulse appears
    :param index_wait: Time to wait, in seconds, for the index pulse
    :return: The actual number of bytes of read
    """
    ...

def mfm_readinto(
    buffer: WriteableBuffer,
    flux: ReadableBuffer,
    flux_t2_max: int,
    flux_t3_max: int,
    validity: bytearray | None = None,
    clear_validity: bool = True,
) -> int:
    """Decode MFM flux into the buffer

    The track is assumed to consist of 512-byte sectors.

    The function returns the number of sectors successfully read. In addition,
    it updates the ``validity`` buffer with information about which sectors
    were read.

    MFM encoding uses pulses of 3 widths, "T2", "T3" and "T4".
    A 1440KiB disk in standard MFM format has "T2" pulses of 2000ns, "T3" pulses of 3000ns,
    and "T4" pulses of 4000ns.

    Parameters ``t2_max`` and ``t3_max`` are used to distinguish these pulses.
    A pulse with ``p <= t2_max`` is a "T2" pulse,
    a pulse with ``t2_max < p <= t3_max`` is a "T3" pulse,
    and a pulse with ``t3_max < p`` is a "T4" pulse.

    The following code can convert a number in nanoseconds to a number of samples
    for a given sample rate:

    .. code-block:: py

        def ns_to_count(ns, samplerate):
            return round(ns * samplerate * 1e-9)

    This means the following typical values are a good starting place for a 1.44MB floppy:

    .. code-block:: py

        t2_max = ns_to_count(2500, samplerate) # Mid way between T2 and T3 length
        t3_max = ns_to_count(3500, samplerate) # Mid way between T2 and T3 length

    :param buffer: Read data into this buffer.  Byte length must be a multiple of 512.
    :param flux: Flux data from a previous `flux_readinto` call
    :param t2_max: Maximum time of a flux cell in counts.
    :param t3_max: Nominal time of a flux cell in counts.
    :param validity: Optional bytearray. For each sector successfully read, the corresponding validity entry is set to ``1`` and previously valid sectors are not decoded.
    :param clear_validity: If `True`, clear the validity information before decoding and attempt to decode all sectors.
    :return: The actual number of sectors read
    """
    ...

samplerate: int
"""The approximate sample rate in Hz used by flux_readinto."""
