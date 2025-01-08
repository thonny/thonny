"""Memory monitoring helpers"""

from __future__ import annotations

from typing import Optional

class AllocationError(Exception):
    """Catchall exception for allocation related errors."""

    ...

class AllocationAlarm:
    def __init__(self, *, minimum_block_count: int = 1) -> None:
        """Throw an exception when an allocation of ``minimum_block_count`` or more blocks
           occurs while active.

        Track allocations::

          import memorymonitor

          aa = memorymonitor.AllocationAlarm(minimum_block_count=2)
          x = 2
          # Should not allocate any blocks.
          with aa:
              x = 5

          # Should throw an exception when allocating storage for the 20 bytes.
          with aa:
              x = bytearray(20)

        """
        ...

    def ignore(self, count: int) -> AllocationAlarm:
        """Sets the number of applicable allocations to ignore before raising the exception.
        Automatically set back to zero at context exit.

        Use it within a ``with`` block::

          # Will not alarm because the bytearray allocation will be ignored.
          with aa.ignore(2):
              x = bytearray(20)
        """
        ...

    def __enter__(self) -> AllocationAlarm:
        """Enables the alarm."""
        ...

    def __exit__(self) -> None:
        """Automatically disables the allocation alarm when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

class AllocationSize:
    def __init__(self) -> None:
        """Tracks the number of allocations in power of two buckets.

        It will have 16 16-bit buckets to track allocation counts. It is total allocations
        meaning frees are ignored. Reallocated memory is counted twice, at allocation and when
        reallocated with the larger size.

        The buckets are measured in terms of blocks which is the finest granularity of the heap.
        This means bucket 0 will count all allocations less than or equal to the number of bytes
        per block, typically 16. Bucket 2 will be less than or equal to 4 blocks. See
        `bytes_per_block` to convert blocks to bytes.

        Multiple AllocationSizes can be used to track different code boundaries.

        Track allocations::

          import memorymonitor

          mm = memorymonitor.AllocationSize()
          with mm:
            print("hello world" * 3)

          for bucket, count in enumerate(mm):
              print("<", 2 ** bucket, count)

        """
        ...

    def __enter__(self) -> AllocationSize:
        """Clears counts and resumes tracking."""
        ...

    def __exit__(self) -> None:
        """Automatically pauses allocation tracking when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    bytes_per_block: int
    """Number of bytes per block"""
    def __len__(self) -> int:
        """Returns the number of allocation buckets.

        This allows you to::

          mm = memorymonitor.AllocationSize()
          print(len(mm))"""
        ...

    def __getitem__(self, index: int) -> Optional[int]:
        """Returns the allocation count for the given bucket.

        This allows you to::

          mm = memorymonitor.AllocationSize()
          print(mm[0])"""
        ...
