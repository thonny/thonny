from __future__ import annotations

from typing import Callable

def bisect(
    fun: Callable[[float], float],
    a: float,
    b: float,
    *,
    xtol: float = 2.4e-7,
    maxiter: int = 100,
) -> float:
    """
    :param callable f: The function to bisect
    :param float a: The left side of the interval
    :param float b: The right side of the interval
    :param float xtol: The tolerance value
    :param float maxiter: The maximum number of iterations to perform

    Find a solution (zero) of the function ``f(x)`` on the interval
    (``a``..``b``) using the bisection method.  The result is accurate to within
    ``xtol`` unless more than ``maxiter`` steps are required."""
    ...

def fmin(
    fun: Callable[[float], float],
    x0: float,
    *,
    xatol: float = 2.4e-7,
    fatol: float = 2.4e-7,
    maxiter: int = 200,
) -> float:
    """
    :param callable f: The function to bisect
    :param float x0: The initial x value
    :param float xatol: The absolute tolerance value
    :param float fatol: The relative tolerance value

    Find a minimum of the function ``f(x)`` using the downhill simplex method.
    The located ``x`` is within ``fxtol`` of the actual minimum, and ``f(x)``
    is within ``fatol`` of the actual minimum unless more than ``maxiter``
    steps are requried."""
    ...

def newton(
    fun: Callable[[float], float],
    x0: float,
    *,
    xtol: float = 2.4e-7,
    rtol: float = 0.0,
    maxiter: int = 50,
) -> float:
    """
    :param callable f: The function to bisect
    :param float x0: The initial x value
    :param float xtol: The absolute tolerance value
    :param float rtol: The relative tolerance value
    :param float maxiter: The maximum number of iterations to perform

    Find a solution (zero) of the function ``f(x)`` using Newton's Method.
    The result is accurate to within ``xtol * rtol * |f(x)|`` unless more than
    ``maxiter`` steps are requried."""
    ...
