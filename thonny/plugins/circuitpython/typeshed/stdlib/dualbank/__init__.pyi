"""Dualbank Module

The `dualbank` module adds ability to update and switch between the
two identical app partitions, which can contain different firmware versions.

Having two partitions enables rollback functionality.

The two partitions are defined as the boot partition and the next-update partition.
Calling `dualbank.flash()` writes the next-update partition.

After the next-update partition is written a validation check is performed
and on a successful validation this partition is set as the boot partition.
On next reset, firmware will be loaded from this partition.

Use cases:
    * Can be used for ``OTA`` Over-The-Air updates.
    * Can be used for ``dual-boot`` of different firmware versions or platforms.

.. note::

    Boards with flash ``=2MB``:
        This module is unavailable as the flash is only large enough for one app partition.

    Boards with flash ``>2MB``:
        This module is enabled/disabled at runtime based on whether the ``CIRCUITPY`` drive
        is extended or not. See `storage.erase_filesystem()` for more information.

.. code-block:: python

    import dualbank

    dualbank.flash(buffer, offset)
    dualbank.switch()
"""

from __future__ import annotations

from circuitpython_typing import ReadableBuffer

...

def flash(buffer: ReadableBuffer, offset: int = 0) -> None:
    """Writes one of the two app partitions at the given offset.

    This can be called multiple times when flashing the firmware in smaller chunks.

    :param ReadableBuffer buffer: The entire firmware or a partial chunk.
    :param int offset: Start writing at this offset in the app partition.
    """
    ...

def switch() -> None:
    """Switches to the next-update partition.

    On next reset, firmware will be loaded from the partition just switched over to.
    """
    ...
