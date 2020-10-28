"""Stack information and analysis"""

def max_stack_usage() -> int:
    """Return the maximum excursion of the stack so far."""
    ...

def stack_size() -> int:
    """Return the size of the entire stack.
    Same as in micropython.mem_info(), but returns a value instead
    of just printing it."""
    ...

def stack_usage() -> Any:
    """Return how much stack is currently in use.
    Same as micropython.stack_use(); duplicated here for convenience."""
    ...

