class StopWatch:
    """
    A stopwatch to measure time intervals. Similar to the stopwatch feature on your phone.
    """

    def __init__(self):
        ...

    def time(self) -> int:
        """
        Gets the current time of the stopwatch.

        Returns:
            Elapsed time in milliseconds.
        """
        return 0

    def pause(self):
        """
        Pauses the stopwatch.
        """
        ...

    def resume(self):
        """
        Resumes the stopwatch.
        """
        ...

    def reset(self):
        """
        Reset the stopwatch time to 0. 

        Note:
            The run state is unaffected:
                - If it was paused, it stays paused (but now at 0).
                - If it was running, it stays running (but starting again from 0)
        """
        ...
