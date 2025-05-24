from __future__ import annotations

import builtins

import ulab
import ulab.numpy

def real(val: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    Return the real part of the complex argument, which can be
    either an ndarray, or a scalar."""
    ...

def imag(val: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    Return the imaginary part of the complex argument, which can be
    either an ndarray, or a scalar."""
    ...

def conjugate(
    val: builtins.complex | ulab.numpy.ndarray,
) -> builtins.complex | ulab.numpy.ndarray:
    """
    Return the conjugate of the complex argument, which can be
    either an ndarray, or a scalar."""
    ...

def sort_complex(a: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    .. param: a
      a one-dimensional ndarray

    Sort a complex array using the real part first, then the imaginary part.
    Always returns a sorted complex array, even if the input was real."""
    ...

def abs(a: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    .. param: a
      a one-dimensional ndarray

    Return the absolute value of complex ndarray."""
    ...
