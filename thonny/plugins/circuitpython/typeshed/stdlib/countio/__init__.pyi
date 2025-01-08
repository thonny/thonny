"""Support for edge counting

The `countio` module contains logic to read and count edge transitions

For more information on the applications of counting edges, see
`this Learn Guide on sequential circuits
<https://learn.adafruit.com/digital-circuits-4-sequential-circuits>`_.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info."""

from __future__ import annotations

from typing import Optional

import digitalio
import microcontroller

class Edge:
    """Enumerates which signal transitions can be counted."""

    def __init__(self) -> None:
        """Enum-like class to define which signal transitions to count."""
        ...
    RISE: Edge
    """Count the rising edges."""

    FALL: Edge
    """Count the falling edges."""

    RISE_AND_FALL: Edge
    """Count the rising and falling edges.

    **Limitations:** ``RISE_AND_FALL`` is not available to RP2040 due to hardware limitations.
    """

class Counter:
    """Count the number of rising- and/or falling-edge transitions on a given pin."""

    def __init__(
        self,
        pin: microcontroller.Pin,
        *,
        edge: Edge = Edge.FALL,
        pull: Optional[digitalio.Pull] = None,
    ) -> None:
        """Create a Counter object associated with the given pin that counts
        rising- and/or falling-edge transitions. At least one of ``rise`` and ``fall`` must be True.
        The default is to count only falling edges, and is for historical backward compatibility.

        :param ~microcontroller.Pin pin: pin to monitor
        :param Edge edge: which edge transitions to count
        :param Optional[digitalio.Pull] pull: enable a pull-up or pull-down if not None


        For example::

            import board
            import countio

            # Count rising edges only.
            pin_counter = countio.Counter(board.D1, edge=countio.Edge.RISE)
            # Reset the count after 100 counts.
            while True:
                if pin_counter.count >= 100:
                    pin_counter.reset()
                print(pin_counter.count)

        **Limitations:** On RP2040, `Counter` uses the PWM peripheral, and
        is limited to using PWM channel B pins due to hardware restrictions.
        See the pin assignments for your board to see which pins can be used.
        """
        ...

    def deinit(self) -> None:
        """Deinitializes the Counter and releases any hardware resources for reuse."""

    def __enter__(self) -> Counter:
        """No-op used by Context Managers."""

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
    count: int
    """The current count in terms of pulses."""
    def reset(self) -> None:
        """Resets the count back to 0."""
