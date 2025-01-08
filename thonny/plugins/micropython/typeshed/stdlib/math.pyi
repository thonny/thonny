"""
mathematical functions.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/math.rst.
=====================================

.. module:: math
   :synopsis: mathematical functions

|see_cpython_module| :mod:`python:math`.

The ``math`` module provides some basic mathematical functions for
working with floating-point numbers.

*Note:* On the pyboard, floating-point numbers have 32-bit precision.

Availability: not available on WiPy. Floating point support required
for this module.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import SupportsFloat, Final

def acos(x: SupportsFloat, /) -> float:
    """
   Return the inverse cosine of ``x``.
   """

def acosh(x: SupportsFloat, /) -> float:
    """
   Return the inverse hyperbolic cosine of ``x``.
   """

def asin(x: SupportsFloat, /) -> float:
    """
   Return the inverse sine of ``x``.
   """

def asinh(x: SupportsFloat, /) -> float:
    """
   Return the inverse hyperbolic sine of ``x``.
   """

def atan(x: SupportsFloat, /) -> float:
    """
   Return the inverse tangent of ``x``.
   """

def atan2(y: SupportsFloat, x: SupportsFloat, /) -> float:
    """
   Return the principal value of the inverse tangent of ``y/x``.
   """

def atanh(x: SupportsFloat, /) -> float:
    """
   Return the inverse hyperbolic tangent of ``x``.
   """

def ceil(x: SupportsFloat, /) -> int:
    """
   Return an integer, being ``x`` rounded towards positive infinity.
   """

def copysign(x: SupportsFloat, y: SupportsFloat, /) -> float:
    """
   Return ``x`` with the sign of ``y``.
   """

def cos(x: SupportsFloat, /) -> float:
    """
   Return the cosine of ``x``.
   """

def cosh(x: SupportsFloat, /) -> float:
    """
   Return the hyperbolic cosine of ``x``.
   """

def degrees(x: SupportsFloat, /) -> float:
    """
   Return radians ``x`` converted to degrees.
   """

def erf(x: SupportsFloat, /) -> float:
    """
   Return the error function of ``x``.
   """

def erfc(x: SupportsFloat, /) -> float:
    """
   Return the complementary error function of ``x``.
   """

def exp(x: SupportsFloat, /) -> float:
    """
   Return the exponential of ``x``.
   """

def expm1(x: SupportsFloat, /) -> float:
    """
   Return ``exp(x) - 1``.
   """

def fabs(x: SupportsFloat, /) -> float:
    """
   Return the absolute value of ``x``.
   """

def floor(x: SupportsFloat, /) -> int:
    """
   Return an integer, being ``x`` rounded towards negative infinity.
   """

def fmod(x: SupportsFloat, y: SupportsFloat, /) -> float:
    """
   Return the remainder of ``x/y``.
   """

def frexp(x: SupportsFloat, /) -> tuple[float, int]:
    """
   Decomposes a floating-point number into its mantissa and exponent.
   The returned value is the tuple ``(m, e)`` such that ``x == m * 2**e``
   exactly.  If ``x == 0`` then the function returns ``(0.0, 0)``, otherwise
   the relation ``0.5 <= abs(m) < 1`` holds.
   """

def gamma(x: SupportsFloat, /) -> float:
    """
   Return the gamma function of ``x``.
   """

def isfinite(x: SupportsFloat, /) -> bool:
    """
   Return ``True`` if ``x`` is finite.
   """

def isinf(x: SupportsFloat, /) -> bool:
    """
   Return ``True`` if ``x`` is infinite.
   """

def isnan(x: SupportsFloat, /) -> bool:
    """
   Return ``True`` if ``x`` is not-a-number
   """

# noinspection PyShadowingNames
def ldexp(x: SupportsFloat, exp: int, /) -> float:
    """
   Return ``x * (2**exp)``.
   """

def lgamma(x: SupportsFloat, /) -> float:
    """
   Return the natural logarithm of the gamma function of ``x``.
   """

def log(x: SupportsFloat, /) -> float:
    """
   Return the natural logarithm of ``x``.
   """

def log10(x: SupportsFloat, /) -> float:
    """
   Return the base-10 logarithm of ``x``.
   """

def log2(x: SupportsFloat, /) -> float:
    """
   Return the base-2 logarithm of ``x``.
   """

def modf(x: SupportsFloat, /) -> tuple[float, float]:
    """
   Return a tuple of two floats, being the fractional and integral parts of
   ``x``.  Both return values have the same sign as ``x``.
   """

def pow(x: SupportsFloat, y: SupportsFloat, /) -> float:
    """
   Returns ``x`` to the power of ``y``.
   """

def radians(x: SupportsFloat, /) -> float:
    """
   Return degrees ``x`` converted to radians.
   """

def sin(x: SupportsFloat, /) -> float:
    """
   Return the sine of ``x``.
   """

def sinh(x: SupportsFloat, /) -> float:
    """
   Return the hyperbolic sine of ``x``.
   """

def sqrt(x: SupportsFloat, /) -> float:
    """
   Return the square root of ``x``.
   """

def tan(x: SupportsFloat, /) -> float:
    """
   Return the tangent of ``x``.
   """

def tanh(x: SupportsFloat, /) -> float:
    """
   Return the hyperbolic tangent of ``x``.
   """

def trunc(x: SupportsFloat, /) -> float:
    """
   Return an integer, being ``x`` rounded towards 0.
   """

e: Final[float] = ...
"""
base of the natural logarithm
"""

pi: Final[float] = ...
"""
the ratio of a circle's circumference to its diameter
"""
