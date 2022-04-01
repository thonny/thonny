"""
mathematical functions for complex numbers.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/cmath.rst.
==========================================================

.. module:: cmath
   :synopsis: mathematical functions for complex numbers

|see_cpython_module| :mod:`python:cmath`.

The ``cmath`` module provides some basic mathematical functions for
working with complex numbers.

Availability: not available on WiPy and ESP8266. Floating point support
required for this module.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import SupportsComplex, SupportsFloat, Final

_C: Final = SupportsFloat | SupportsComplex

def cos(z: _C, /) -> complex:
    """
   Return the cosine of ``z``.
   """

def exp(z: _C, /) -> complex:
    """
   Return the exponential of ``z``.
   """

def log(z: _C, /) -> complex:
    """
   Return the natural logarithm of ``z``.  The branch cut is along the negative real axis.
   """

def log10(z: _C, /) -> complex:
    """
   Return the base-10 logarithm of ``z``.  The branch cut is along the negative real axis.
   """

def phase(z: _C, /) -> float:
    """
   Returns the phase of the number ``z``, in the range (-pi, +pi].
   """

def polar(z: _C, /) -> tuple[float, float]:
    """
   Returns, as a tuple, the polar form of ``z``.
   """

def rect(r: float, phi: float, /) -> complex:
    """
   Returns the complex number with modulus ``r`` and phase ``phi``.
   """

def sin(z: _C, /) -> complex:
    """
   Return the sine of ``z``.
   """

def sqrt(z: _C, /) -> complex:
    """
   Return the square-root of ``z``.
   """

e: Final[float] = ...
"""
base of the natural logarithm
"""

pi: Final[float] = ...
"""
the ratio of a circle's circumference to its diameter
"""
