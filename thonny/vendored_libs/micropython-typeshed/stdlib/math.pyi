"""
Mathematical functions.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/math.html

CPython module: :mod:`python:math` https://docs.python.org/3/library/math.html .

The ``math`` module provides some basic mathematical functions for
working with floating-point numbers.

*Note:* On the pyboard, floating-point numbers have 32-bit precision.

Availability: not available on WiPy. Floating point support required
for this module.

---
Module: 'math' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from _typeshed import Incomplete
from typing import SupportsFloat, Tuple
from typing_extensions import Awaitable, TypeAlias, TypeVar

inf: float = inf
nan: float = nan
pi: float = 3.141593
e: float = 2.718282
tau: float = 6.283185

def ldexp(x: SupportsFloat, exp: int, /) -> float:
    """
    Return ``x * (2**exp)``.
    """
    ...

def lgamma(x: SupportsFloat, /) -> float:
    """
    Return the natural logarithm of the gamma function of ``x``.
    """
    ...

def trunc(x: SupportsFloat, /) -> int:
    """
    Return an integer, being ``x`` rounded towards 0.
    """
    ...

def isclose(*args, **kwargs) -> Incomplete: ...
def gamma(x: SupportsFloat, /) -> float:
    """
    Return the gamma function of ``x``.
    """
    ...

def isnan(x: SupportsFloat, /) -> bool:
    """
    Return ``True`` if ``x`` is not-a-number
    """
    ...

def isfinite(x: SupportsFloat, /) -> bool:
    """
    Return ``True`` if ``x`` is finite.
    """
    ...

def isinf(x: SupportsFloat, /) -> bool:
    """
    Return ``True`` if ``x`` is infinite.
    """
    ...

def sqrt(x: SupportsFloat, /) -> float:
    """
    Return the square root of ``x``.
    """
    ...

def sinh(x: SupportsFloat, /) -> float:
    """
    Return the hyperbolic sine of ``x``.
    """
    ...

def log(x: SupportsFloat, /) -> float:
    """
    With one argument, return the natural logarithm of *x*.

    With two arguments, return the logarithm of *x* to the given *base*.
    """
    ...

def tan(x: SupportsFloat, /) -> float:
    """
    Return the tangent of ``x``.
    """
    ...

def tanh(x: SupportsFloat, /) -> float:
    """
    Return the hyperbolic tangent of ``x``.
    """
    ...

def log2(x: SupportsFloat, /) -> float:
    """
    Return the base-2 logarithm of ``x``.
    """
    ...

def log10(x: SupportsFloat, /) -> float:
    """
    Return the base-10 logarithm of ``x``.
    """
    ...

def sin(x: SupportsFloat, /) -> float:
    """
    Return the sine of ``x``.
    """
    ...

def modf(x: SupportsFloat, /) -> Tuple:
    """
    Return a tuple of two floats, being the fractional and integral parts of
    ``x``.  Both return values have the same sign as ``x``.
    """
    ...

def radians(x: SupportsFloat, /) -> float:
    """
    Return degrees ``x`` converted to radians.
    """
    ...

def atanh(x: SupportsFloat, /) -> float:
    """
    Return the inverse hyperbolic tangent of ``x``.
    """
    ...

def atan2(y: SupportsFloat, x: SupportsFloat, /) -> float:
    """
    Return the principal value of the inverse tangent of ``y/x``.
    """
    ...

def atan(x: SupportsFloat, /) -> float:
    """
    Return the inverse tangent of ``x``.
    """
    ...

def ceil(x: SupportsFloat, /) -> int:
    """
    Return an integer, being ``x`` rounded towards positive infinity.
    """
    ...

def copysign(x: SupportsFloat, y: SupportsFloat, /) -> float:
    """
    Return ``x`` with the sign of ``y``.
    """
    ...

def frexp(x: SupportsFloat, /) -> tuple[float, int]:
    """
    Decomposes a floating-point number into its mantissa and exponent.
    The returned value is the tuple ``(m, e)`` such that ``x == m * 2**e``
    exactly.  If ``x == 0`` then the function returns ``(0.0, 0)``, otherwise
    the relation ``0.5 <= abs(m) < 1`` holds.
    """
    ...

def acos(x: SupportsFloat, /) -> float:
    """
    Return the inverse cosine of ``x``.
    """
    ...

def pow(x: SupportsFloat, y: SupportsFloat, /) -> float:
    """
    Returns ``x`` to the power of ``y``.
    """
    ...

def asinh(x: SupportsFloat, /) -> float:
    """
    Return the inverse hyperbolic sine of ``x``.
    """
    ...

def acosh(x: SupportsFloat, /) -> float:
    """
    Return the inverse hyperbolic cosine of ``x``.
    """
    ...

def asin(x: SupportsFloat, /) -> float:
    """
    Return the inverse sine of ``x``.
    """
    ...

def factorial(*args, **kwargs) -> Incomplete: ...
def fabs(x: SupportsFloat, /) -> float:
    """
    Return the absolute value of ``x``.
    """
    ...

def expm1(x: SupportsFloat, /) -> float:
    """
    Return ``exp(x) - 1``.
    """
    ...

def floor(x: SupportsFloat, /) -> int:
    """
    Return an integer, being ``x`` rounded towards negative infinity.
    """
    ...

def fmod(x: SupportsFloat, y: SupportsFloat, /) -> float:
    """
    Return the remainder of ``x/y``.
    """
    ...

def cos(x: SupportsFloat, /) -> float:
    """
    Return the cosine of ``x``.
    """
    ...

def degrees(x: SupportsFloat, /) -> float:
    """
    Return radians ``x`` converted to degrees.
    """
    ...

def cosh(x: SupportsFloat, /) -> float:
    """
    Return the hyperbolic cosine of ``x``.
    """
    ...

def exp(x: SupportsFloat, /) -> float:
    """
    Return the exponential of ``x``.
    """
    ...

def erf(x: SupportsFloat, /) -> float:
    """
    Return the error function of ``x``.
    """
    ...

def erfc(x: SupportsFloat, /) -> float:
    """
    Return the complementary error function of ``x``.
    """
    ...
