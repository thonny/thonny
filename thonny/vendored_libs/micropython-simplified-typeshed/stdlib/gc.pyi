"""Control the garbage collector"""

from typing import overload

def enable() -> None:
    """Enable automatic garbage collection."""
    ...

def disable() -> None:
    """Disable automatic garbage collection.

    Heap memory can still be allocated,
    and garbage collection can still be initiated manually using ``gc.collect``."""

def collect() -> None:
    """Run a garbage collection."""
    ...

def mem_alloc() -> int:
    """Get the number of bytes of heap RAM that are allocated.

    :return: The number of bytes allocated.

    This function is MicroPython extension.
    """
    ...

def mem_free() -> int:
    """Get the number of bytes of available heap RAM, or -1 if this amount is not known.

    :return: The number of bytes free.

    This function is MicroPython extension.
    """
    ...

@overload
def threshold() -> int:
    """Query the additional GC allocation threshold.

    :return: The GC allocation threshold.

    This function is a MicroPython extension. CPython has a similar
    function - ``set_threshold()``, but due to different GC
    implementations, its signature and semantics are different.
    """
    ...

@overload
def threshold(amount: int) -> None:
    """Set the additional GC allocation threshold.

    Normally, a collection is triggered only when a new allocation
    cannot be satisfied, i.e. on an  out-of-memory (OOM) condition.
    If this function is called, in addition to OOM, a collection
    will be triggered each time after ``amount`` bytes have been
    allocated (in total, since the previous time such an amount of bytes
    have been allocated). ``amount`` is usually specified as less than the
    full heap size, with the intention to trigger a collection earlier than when the
    heap becomes exhausted, and in the hope that an early collection will prevent
    excessive memory fragmentation. This is a heuristic measure, the effect
    of which will vary from application to application, as well as
    the optimal value of the ``amount`` parameter.

    A value of -1 means a disabled allocation threshold.

    This function is a MicroPython extension. CPython has a similar
    function - ``set_threshold()``, but due to different GC
    implementations, its signature and semantics are different.

    :param amount: The number of bytes after which a garbage collection should be triggered.
    """
    ...
