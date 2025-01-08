"""
control the garbage collector.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/gc.rst.
==========================================

.. module:: gc
   :synopsis: control the garbage collector

|see_cpython_module| :mod:`python:gc`.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import overload

def enable() -> None:
    """
   Enable automatic garbage collection.
   """

def disable() -> None:
    """
   Disable automatic garbage collection.  Heap memory can still be allocated,
   and garbage collection can still be initiated manually using :meth:`gc.collect`.
   """

def collect() -> None:
    """
   Run a garbage collection.
   """

def mem_alloc() -> int:
    """
   Return the number of bytes of heap RAM that are allocated.
   
   .. admonition:: Difference to CPython
      :class: attention
   
      This function is MicroPython extension.
   """

def mem_free() -> int:
    """
   Return the number of bytes of available heap RAM, or -1 if this amount
   is not known.
   
   .. admonition:: Difference to CPython
      :class: attention
   
      This function is MicroPython extension.
   """

@overload
def threshold() -> int:
    """
   Set or query the additional GC allocation threshold. Normally, a collection
   is triggered only when a new allocation cannot be satisfied, i.e. on an
   out-of-memory (OOM) condition. If this function is called, in addition to
   OOM, a collection will be triggered each time after *amount* bytes have been
   allocated (in total, since the previous time such an amount of bytes
   have been allocated). *amount* is usually specified as less than the
   full heap size, with the intention to trigger a collection earlier than when the
   heap becomes exhausted, and in the hope that an early collection will prevent
   excessive memory fragmentation. This is a heuristic measure, the effect
   of which will vary from application to application, as well as
   the optimal value of the *amount* parameter.
   
   Calling the function without argument will return the current value of
   the threshold. A value of -1 means a disabled allocation threshold.
   
   .. admonition:: Difference to CPython
      :class: attention
   
      This function is a MicroPython extension. CPython has a similar
      function - ``set_threshold()``, but due to different GC
      implementations, its signature and semantics are different.
   """

@overload
def threshold(amount: int) -> None:
    """
   Set or query the additional GC allocation threshold. Normally, a collection
   is triggered only when a new allocation cannot be satisfied, i.e. on an
   out-of-memory (OOM) condition. If this function is called, in addition to
   OOM, a collection will be triggered each time after *amount* bytes have been
   allocated (in total, since the previous time such an amount of bytes
   have been allocated). *amount* is usually specified as less than the
   full heap size, with the intention to trigger a collection earlier than when the
   heap becomes exhausted, and in the hope that an early collection will prevent
   excessive memory fragmentation. This is a heuristic measure, the effect
   of which will vary from application to application, as well as
   the optimal value of the *amount* parameter.
   
   Calling the function without argument will return the current value of
   the threshold. A value of -1 means a disabled allocation threshold.
   
   .. admonition:: Difference to CPython
      :class: attention
   
      This function is a MicroPython extension. CPython has a similar
      function - ``set_threshold()``, but due to different GC
      implementations, its signature and semantics are different.
   """
