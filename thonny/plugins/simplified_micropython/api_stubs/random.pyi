from typing import Sequence, TypeVar, overload

_T = TypeVar('_T')


def choice(seq: Sequence[_T]) -> _T:
    """
    Return a random element from the non-empty sequence seq. If seq is empty, raises IndexError.
    """


def getrandbits(n: int) -> int:
    """
    Returns an integer with n random bits.

    Because the underlying generator function returns at most 30 bits, n may only be a value between 1-30 (inclusive).
    """


def randint(a: int, b: int) -> int:
    """
    Return a random integer N such that a <= N <= b. Alias for randrange(a, b+1).
    """


def random() -> float:
    """
    Return the next random floating point number in the range [0.0, 1.0).
    """


@overload
def randrange(stop: int) -> int:
    """
    Return a randomly selected integer between zero and up to (but not including) stop.
    """

@overload
def randrange(start: int, stop: int) -> int:
    """
    Return a randomly selected integer from range(start, stop).
    """

@overload
def randrange(start: int, stop: int, step: int) -> int:
    """
    Return a randomly selected element from range(start, stop, step).
    """


def seed(n: int) -> None:
    """
    Initialize the random number generator with a known integer n. This will give you reproducibly deterministic randomness from a given starting state (n).
    """


def uniform(a: float, b: float) -> float:
    """
    Return a random floating point number N such that a <= N <= b for a <= b and b <= N <= a for b < a.
    """
