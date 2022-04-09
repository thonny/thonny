"""DUALBANK Module

The `dualbank` module adds ability to update and switch
between the two app partitions.

There are two identical partitions, these contain different
firmware versions.
Having two partitions enables rollback functionality.

The two partitions are defined as boot partition and
next-update partition. Calling `dualbank.flash()` writes
the next-update partition.

After the next-update partition is written a validation
check is performed and on a successful validation this
partition is set as the boot partition. On next reset,
firmware will be loaded from this partition.

Here is the sequence of commands to follow:

.. code-block:: python

    import dualbank

    dualbank.flash(buffer, offset)
    dualbank.switch()
"""

from __future__ import annotations

from circuitpython_typing import ReadableBuffer

...

def flash(*buffer: ReadableBuffer, offset: int = 0) -> None:
    """Writes one of two app partitions at the given offset.

    This can be called multiple times when flashing the firmware
    in small chunks.
    """
    ...

def switch() -> None:
    """Switches the boot partition.

    On next reset, firmware will be loaded from the partition
    just switched over to.
    """
    ...
