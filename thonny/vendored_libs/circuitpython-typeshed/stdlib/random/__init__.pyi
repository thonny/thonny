"""pseudo-random numbers and choices

|see_cpython_module| :mod:`cpython:random`.

Like its CPython cousin, CircuitPython's random seeds itself on first use
with a true random from os.urandom() when available or the uptime otherwise.
Once seeded, it will be deterministic, which is why its bad for cryptography.

.. warning:: Numbers from this module are not cryptographically strong! Use
  bytes from `os.urandom` directly for true randomness."""

from __future__ import annotations

from typing import Sequence, TypeVar, overload

_T = TypeVar("_T")

def seed(seed: int) -> None:
    """Sets the starting seed of the random  number generation. Further calls to
    `random` will return deterministic results afterwards."""
    ...

def getrandbits(k: int) -> int:
    """Returns an integer with *k* random bits."""
    ...

@overload
def randrange(stop: int) -> int: ...
@overload
def randrange(start: int, stop: int) -> int: ...
@overload
def randrange(start: int, stop: int, step: int) -> int:
    """Returns a randomly selected integer from ``range(start[, stop[, step]])``."""
    ...

def randint(a: int, b: int) -> int:
    """Returns a randomly selected integer between a and b inclusive. Equivalent
    to ``randrange(a, b + 1, 1)``"""
    ...

def choice(seq: Sequence[_T]) -> _T:
    """Returns a randomly selected element from the given sequence. Raises
    IndexError when the sequence is empty."""
    ...

def random() -> float:
    """Returns a random float between 0 and 1.0."""
    ...

def uniform(a: float, b: float) -> float:
    """Returns a random float between a and b. It may or may not be inclusive
    depending on float rounding."""
    ...
