"""pseudo-random numbers and choices

The `random` module is a strict subset of the CPython `cpython:random`
module. So, code written in CircuitPython will work in CPython but not
necessarily the other way around.

Like its CPython cousin, CircuitPython's random seeds itself on first use
with a true random from os.urandom() when available or the uptime otherwise.
Once seeded, it will be deterministic, which is why its bad for cryptography.

.. warning:: Numbers from this module are not cryptographically strong! Use
  bytes from `os.urandom` directly for true randomness."""

def seed(seed: Any) -> Any:
    """Sets the starting seed of the random  number generation. Further calls to
    `random` will return deterministic results afterwards."""
    ...

def getrandbits(k: Any) -> Any:
    """Returns an integer with *k* random bits."""
    ...

def randrange(stop: Any) -> Any:
    """Returns a randomly selected integer from ``range(start, stop, step)``."""
    ...

def randint(a: Any, b: Any) -> Any:
    """Returns a randomly selected integer between a and b inclusive. Equivalent
    to ``randrange(a, b + 1, 1)``"""
    ...

def choice(seq: Any) -> Any:
    """Returns a randomly selected element from the given sequence. Raises
    IndexError when the sequence is empty."""
    ...

def random() -> Any:
    """Returns a random float between 0 and 1.0."""
    ...

def uniform(a: Any, b: Any) -> Any:
    """Returns a random float between a and b. It may or may not be inclusive
    depending on float rounding."""
    ...

