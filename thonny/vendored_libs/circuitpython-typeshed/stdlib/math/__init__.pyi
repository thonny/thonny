"""mathematical functions

The `math` module provides some basic mathematical functions for
working with floating-point numbers.

|see_cpython_module| :mod:`cpython:math`.
"""

from __future__ import annotations

from typing import Tuple

e: float
"""base of the natural logarithm"""

pi: float
"""the ratio of a circle's circumference to its diameter"""

def acos(x: float) -> float:
    """Return the inverse cosine of ``x``."""
    ...

def asin(x: float) -> float:
    """Return the inverse sine of ``x``."""
    ...

def atan(x: float) -> float:
    """Return the inverse tangent of ``x``."""
    ...

def atan2(y: float, x: float) -> float:
    """Return the principal value of the inverse tangent of ``y/x``."""
    ...

def ceil(x: float) -> int:
    """Return an integer, being ``x`` rounded towards positive infinity."""
    ...

def copysign(x: float, y: float) -> float:
    """Return ``x`` with the sign of ``y``."""
    ...

def cos(x: float) -> float:
    """Return the cosine of ``x``."""
    ...

def degrees(x: float) -> float:
    """Return radians ``x`` converted to degrees."""
    ...

def exp(x: float) -> float:
    """Return the exponential of ``x``."""
    ...

def fabs(x: float) -> float:
    """Return the absolute value of ``x``."""
    ...

def floor(x: float) -> int:
    """Return an integer, being ``x`` rounded towards negative infinity."""
    ...

def fmod(x: float, y: float) -> int:
    """Return the remainder of ``x/y``."""
    ...

def frexp(x: float) -> Tuple[int, int]:
    """Decomposes a floating-point number into its mantissa and exponent.
    The returned value is the tuple ``(m, e)`` such that ``x == m * 2**e``
    exactly.  If ``x == 0`` then the function returns ``(0.0, 0)``, otherwise
    the relation ``0.5 <= abs(m) < 1`` holds."""
    ...

def isfinite(x: float) -> bool:
    """Return ``True`` if ``x`` is finite."""
    ...

def isinf(x: float) -> bool:
    """Return ``True`` if ``x`` is infinite."""
    ...

def isnan(x: float) -> bool:
    """Return ``True`` if ``x`` is not-a-number"""
    ...

def ldexp(x: float, exp: float) -> float:
    """Return ``x * (2**exp)``."""
    ...

def log(x: float, base: float = e) -> float:
    """Return the logarithm of x to the given base. If base is not specified,
    returns the natural logarithm (base e) of x"""
    ...

def modf(x: float) -> Tuple[float, float]:
    """Return a tuple of two floats, being the fractional and integral parts of
    ``x``.  Both return values have the same sign as ``x``."""
    ...

def pow(x: float, y: float) -> float:
    """Returns ``x`` to the power of ``y``."""

def radians(x: float) -> float:
    """Return degrees ``x`` converted to radians."""

def sin(x: float) -> float:
    """Return the sine of ``x``."""
    ...

def sqrt(x: float) -> float:
    """Returns the square root of ``x``."""
    ...

def tan(x: float) -> float:
    """Return the tangent of ``x``."""
    ...

def trunc(x: float) -> int:
    """Return an integer, being ``x`` rounded towards 0."""
    ...

def expm1(x: float) -> float:
    """Return ``exp(x) - 1``.

    May not be available on some boards.
    """
    ...

def log2(x: float) -> float:
    """Return the base-2 logarithm of ``x``.

    May not be available on some boards.
    """
    ...

def log10(x: float) -> float:
    """Return the base-10 logarithm of ``x``.

    May not be available on some boards.
    """
    ...

def cosh(x: float) -> float:
    """Return the hyperbolic cosine of ``x``.

    May not be available on some boards.
    """
    ...

def sinh(x: float) -> float:
    """Return the hyperbolic sine of ``x``.

    May not be available on some boards.
    """
    ...

def tanh(x: float) -> float:
    """Return the hyperbolic tangent of ``x``.

    May not be available on some boards.
    """
    ...

def acosh(x: float) -> float:
    """Return the inverse hyperbolic cosine of ``x``.

    May not be available on some boards.
    """
    ...

def asinh(x: float) -> float:
    """Return the inverse hyperbolic sine of ``x``.

    May not be available on some boards.
    """
    ...

def atanh(x: float) -> float:
    """Return the inverse hyperbolic tangent of ``x``.

    May not be available on some boards.
    """
    ...

def erf(x: float) -> float:
    """Return the error function of ``x``.

    May not be available on some boards.
    """
    ...

def erfc(x: float) -> float:
    """Return the complementary error function of ``x``.

    May not be available on some boards.
    """
    ...

def gamma(x: float) -> float:
    """Return the gamma function of ``x``.

    May not be available on some boards.
    """
    ...

def lgamma(x: float) -> float:
    """Return the natural logarithm of the gamma function of ``x``.

    May not be available on some boards.
    """
    ...

def dist(p: tuple, q: tuple) -> float:
    """Return the Euclidean distance between two points ``p`` and ``q``.

    May not be available on some boards.
    """
    ...
