from __future__ import annotations

import ulab
import ulab.numpy
import ulab.scipy

"""Linear algebra functions"""

def solve_triangular(
    A: ulab.numpy.ndarray, b: ulab.numpy.ndarray, lower: bool
) -> ulab.numpy.ndarray:
    """
    :param ~ulab.numpy.ndarray A: a matrix
    :param ~ulab.numpy.ndarray b: a vector
    :param ~bool lower: if true, use only data contained in lower triangle of A, else use upper triangle of A
    :return: solution to the system A x = b. Shape of return matches b
    :raises TypeError: if A and b are not of type ndarray and are not dense
    :raises ValueError: if A is a singular matrix

    Solve the equation A x = b for x, assuming A is a triangular matrix"""
    ...

def cho_solve(L: ulab.numpy.ndarray, b: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    :param ~ulab.numpy.ndarray L: the lower triangular, Cholesky factorization of A
    :param ~ulab.numpy.ndarray b: right-hand-side vector b
    :return: solution to the system A x = b. Shape of return matches b
    :raises TypeError: if L and b are not of type ndarray and are not dense

    Solve the linear equations A x = b, given the Cholesky factorization of A as input
    """
    ...
