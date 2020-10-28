"""mathematical functions

The `math` module provides some basic mathematical functions for
working with floating-point numbers."""

e: Any = ...
"""base of the natural logarithm"""

pi: Any = ...
"""the ratio of a circle's circumference to its diameter"""

def acos(x: Any) -> Any:
    """Return the inverse cosine of ``x``."""
    ...

def asin(x: Any) -> Any:
    """Return the inverse sine of ``x``."""
    ...

def atan(x: Any) -> Any:
    """Return the inverse tangent of ``x``."""
    ...

def atan2(y: Any, x: Any) -> Any:
    """Return the principal value of the inverse tangent of ``y/x``."""
    ...

def ceil(x: Any) -> Any:
    """Return an integer, being ``x`` rounded towards positive infinity."""
    ...

def copysign(x: Any, y: Any) -> Any:
    """Return ``x`` with the sign of ``y``."""
    ...

def cos(x: Any) -> Any:
    """Return the cosine of ``x``."""
    ...

def degrees(x: Any) -> Any:
    """Return radians ``x`` converted to degrees."""
    ...

def exp(x: Any) -> Any:
    """Return the exponential of ``x``."""
    ...

def fabs(x: Any) -> Any:
    """Return the absolute value of ``x``."""
    ...

def floor(x: Any) -> Any:
    """Return an integer, being ``x`` rounded towards negative infinity."""
    ...

def fmod(x: Any, y: Any) -> Any:
    """Return the remainder of ``x/y``."""
    ...

def frexp(x: Any) -> Any:
    """Decomposes a floating-point number into its mantissa and exponent.
    The returned value is the tuple ``(m, e)`` such that ``x == m * 2**e``
    exactly.  If ``x == 0`` then the function returns ``(0.0, 0)``, otherwise
    the relation ``0.5 <= abs(m) < 1`` holds."""
    ...

def isfinite(x: Any) -> Any:
    """Return ``True`` if ``x`` is finite."""
    ...

def isinf(x: Any) -> Any:
    """Return ``True`` if ``x`` is infinite."""
    ...

def isnan(x: Any) -> Any:
    """Return ``True`` if ``x`` is not-a-number"""
    ...

def ldexp(x: Any, exp: Any) -> Any:
    """Return ``x * (2**exp)``."""
    ...

def modf(x: Any) -> Any:
    """Return a tuple of two floats, being the fractional and integral parts of
    ``x``.  Both return values have the same sign as ``x``."""
    ...

def pow(x: Any, y: Any) -> Any:
    """Returns ``x`` to the power of ``y``."""

def radians(x: Any) -> Any:
    """Return degrees ``x`` converted to radians."""

def sin(x: Any) -> Any:
    """Return the sine of ``x``."""
    ...

def sqrt(x: Any) -> Any:
    """Returns the square root of ``x``."""
    ...

def tan(x: Any) -> Any:
    """Return the tangent of ``x``."""
    ...

def trunc(x: Any) -> Any:
    """Return an integer, being ``x`` rounded towards 0."""
    ...

def expm1(x):
    """Return ``exp(x) - 1``."""
    ...

def log2(x):
    """Return the base-2 logarithm of ``x``."""
    ...

def log10(x):
    """Return the base-10 logarithm of ``x``."""
    ...

def cosh(x):
    """Return the hyperbolic cosine of ``x``."""
    ...

def sinh(x):
    """Return the hyperbolic sine of ``x``."""
    ...

def tanh(x):
    """Return the hyperbolic tangent of ``x``."""
    ...

def acosh(x):
    """Return the inverse hyperbolic cosine of ``x``."""
    ...

def asinh(x):
    """Return the inverse hyperbolic sine of ``x``."""
    ...

def atanh(x):
    """Return the inverse hyperbolic tangent of ``x``."""
    ...

def erf(x):
    """Return the error function of ``x``."""
    ...

def erfc(x):
    """Return the complementary error function of ``x``."""
    ...

def gamma(x):
    """Return the gamma function of ``x``."""
    ...

def lgamma(x):
    """Return the natural logarithm of the gamma function of ``x``."""
    ...

