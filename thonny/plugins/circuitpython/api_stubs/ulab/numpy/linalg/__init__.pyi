from __future__ import annotations

from typing import Tuple

import ulab
import ulab.numpy

"""Linear algebra functions"""

def cholesky(A: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    :param ~ulab.numpy.ndarray A: a positive definite, symmetric square matrix
    :return ~ulab.numpy.ndarray L: a square root matrix in the lower triangular form
    :raises ValueError: If the input does not fulfill the necessary conditions

    The returned matrix satisfies the equation m=LL*"""
    ...

def det(m: ulab.numpy.ndarray) -> float:
    """
    :param: m, a square matrix
    :return float: The determinant of the matrix

    Computes the eigenvalues and eigenvectors of a square matrix"""
    ...

def eig(m: ulab.numpy.ndarray) -> Tuple[ulab.numpy.ndarray, ulab.numpy.ndarray]:
    """
    :param m: a square matrix
    :return tuple (eigenvectors, eigenvalues):

    Computes the eigenvalues and eigenvectors of a square matrix"""
    ...

def inv(m: ulab.numpy.ndarray) -> ulab.numpy.ndarray:
    """
    :param ~ulab.numpy.ndarray m: a square matrix
    :return: The inverse of the matrix, if it exists
    :raises ValueError: if the matrix is not invertible

    Computes the inverse of a square matrix"""
    ...

def norm(x: ulab.numpy.ndarray) -> float:
    """
    :param ~ulab.numpy.ndarray x: a vector or a matrix

    Computes the 2-norm of a vector or a matrix, i.e., ``sqrt(sum(x*x))``, however, without the RAM overhead."""
    ...

def qr(m: ulab.numpy.ndarray) -> Tuple[ulab.numpy.ndarray, ulab.numpy.ndarray]:
    """
    :param m: a matrix
    :return tuple (Q, R):

    Factor the matrix a as QR, where Q is orthonormal and R is upper-triangular.
    """
    ...
