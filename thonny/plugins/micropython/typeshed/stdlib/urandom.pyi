"""
random numbers.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/random.rst.
========================================

.. module:: random
   :synopsis: random numbers

This module implements a pseudo-random number generator (PRNG).

|see_cpython_module| :mod:`python:random` .

.. note::

   The following notation is used for intervals:

   - () are open interval brackets and do not include their endpoints.
     For example, (0, 1) means greater than 0 and less than 1.
     In set notation: (0, 1) = {x | 0 < x < 1}.

   - [] are closed interval brackets which include all their limit points.
     For example, [0, 1] means greater than or equal to 0 and less than
     or equal to 1.
     In set notation: [0, 1] = {x | 0 <= x <= 1}.

.. note::

   The :func:`randrange`, :func:`randint` and :func:`choice` functions are only
   available if the ``MICROPY_PY_URANDOM_EXTRA_FUNCS`` configuration option is
   enabled.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import TypeVar, runtime_checkable, Protocol, overload

_T = TypeVar("_T")
@runtime_checkable
class Subscriptable(Protocol[_T]):
    """A `Protocol` (structurally typed) for an object that is subscriptable and of finite length."""

    __slots__ = ()
    def __len__(self) -> int:
        """Number of elements, normally called via `len(x)` where `x` is an object that implements this protocol."""
    def __getitem__(self, index: int) -> _T:
        """
        Element at the given index, 
        normally called via `x[index]` where `x` is an object that implements this protocol.
        """

def getrandbits(n: int, /) -> int:
    """
    Return an integer with *n* random bits (0 <= n <= 32).
   """

def randint(a: int, b: int, /) -> int:
    """
    Return a random integer in the range [*a*, *b*].
   """

@overload
def randrange(stop: int, /) -> int:
    """
    The first form returns a random integer from the range [0, *stop*).
    The second form returns a random integer from the range [*start*, *stop*).
    The third form returns a random integer from the range [*start*, *stop*) in
    steps of *step*.  For instance, calling ``randrange(1, 10, 2)`` will
    return odd numbers between 1 and 9 inclusive.
   """

@overload
def randrange(start: int, stop: int, /) -> int:
    """
    The first form returns a random integer from the range [0, *stop*).
    The second form returns a random integer from the range [*start*, *stop*).
    The third form returns a random integer from the range [*start*, *stop*) in
    steps of *step*.  For instance, calling ``randrange(1, 10, 2)`` will
    return odd numbers between 1 and 9 inclusive.
   """

@overload
def randrange(start: int, stop: int, step: int, /) -> int:
    """
    The first form returns a random integer from the range [0, *stop*).
    The second form returns a random integer from the range [*start*, *stop*).
    The third form returns a random integer from the range [*start*, *stop*) in
    steps of *step*.  For instance, calling ``randrange(1, 10, 2)`` will
    return odd numbers between 1 and 9 inclusive.
   """

def random() -> float:
    """
    Return a random floating point number in the range [0.0, 1.0).
   """

def uniform(a: float, b: float) -> float:
    """
    Return a random floating point number N such that *a* <= N <= *b* for *a* <= *b*,
    and *b* <= N <= *a* for *b* < *a*.
   """

def seed(n: int | None = None, /) -> None:
    """
    Initialise the random number generator module with the seed *n* which should
    be an integer.  When no argument (or ``None``) is passed in it will (if
    supported by the port) initialise the PRNG with a true random number
    (usually a hardware generated random number).
    
    The ``None`` case only works if ``MICROPY_PY_URANDOM_SEED_INIT_FUNC`` is
    enabled by the port, otherwise it raises ``ValueError``.
   """

def choice(sequence: Subscriptable, /) -> None:
    """
    Chooses and returns one item at random from *sequence* (tuple, list or
    any object that supports the subscript operation).
   """
