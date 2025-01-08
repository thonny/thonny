"""
heap queue algorithm.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/heapq.rst.
====================================

.. module:: heapq
   :synopsis: heap queue algorithm

|see_cpython_module| :mod:`python:heapq`.

This module implements the
`min heap queue algorithm <https://en.wikipedia.org/wiki/Heap_%28data_structure%29>`_.

A heap queue is essentially a list that has its elements stored in such a way
that the first item of the list is always the smallest.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import TypeVar, Any, Final

_T: Final = TypeVar("_T")

def heappush(heap: list[_T], item: _T, /) -> None:
    """
   Push the ``item`` onto the ``heap``.
   """

def heappop(heap: list[_T], /) -> _T:
    """
   Pop the first item from the ``heap``, and return it.  Raise ``IndexError`` if
   ``heap`` is empty.
   
   The returned item will be the smallest item in the ``heap``.
   """

def heapify(x: list[Any], /) -> None:
    """
   Convert the list ``x`` into a heap.  This is an in-place operation.
   """
