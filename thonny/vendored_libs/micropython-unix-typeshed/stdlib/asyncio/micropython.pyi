class ThreadSafeFlag:
    """
    class ThreadSafeFlag
    --------------------
    """

    state: int
    def __init__(self) -> None:
        """
        Create a new flag which can be used to synchronise a task with code running
        outside the asyncio loop, such as other threads, IRQs, or scheduler
        callbacks.  Flags start in the cleared state.
        """

    def ioctl(self, req, flags): ...
    def set(self) -> None:
        """
        Set the flag.  If there is a task waiting on the flag, it will be scheduled
        to run.
        """
        ...

    def clear(self) -> None:
        """
        Clear the flag. This may be used to ensure that a possibly previously-set
        flag is clear before waiting for it.
        """
        ...

    async def wait(self) -> Generator[Incomplete]:
        """
        Wait for the flag to be set.  If the flag is already set then it returns
        immediately.  The flag is automatically reset upon return from ``wait``.

        A flag may only be waited on by a single task at a time.

        This is a coroutine.
        """
        ...
