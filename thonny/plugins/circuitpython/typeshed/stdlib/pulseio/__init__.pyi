"""Support for individual pulse based protocols

The `pulseio` module contains classes to provide access to basic pulse IO.
Individual pulses are commonly used in infrared remotes and in DHT
temperature sensors.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info."""

from __future__ import annotations

from typing import Optional

import microcontroller
from circuitpython_typing import ReadableBuffer

class PulseIn:
    """Measure a series of active and idle pulses. This is commonly used in infrared receivers
    and low cost temperature sensors (DHT). The pulsed signal consists of timed active and
    idle periods. Unlike PWM, there is no set duration for active and idle pairs."""

    def __init__(
        self, pin: microcontroller.Pin, maxlen: int = 2, *, idle_state: bool = False
    ) -> None:
        """Create a PulseIn object associated with the given pin. The object acts as
        a read-only sequence of pulse lengths with a given max length. When it is
        active, new pulse lengths are added to the end of the list. When there is
        no more room (len() == `maxlen`) the oldest pulse length is removed to
        make room.

        :param ~microcontroller.Pin pin: Pin to read pulses from.
        :param int maxlen: Maximum number of pulse durations to store at once
        :param bool idle_state: Idle state of the pin. At start and after `resume`
          the first recorded pulse will the opposite state from idle.

        Read a short series of pulses::

          import pulseio
          import board

          pulses = pulseio.PulseIn(board.D7)

          # Wait for an active pulse
          while len(pulses) == 0:
              pass
          # Pause while we do something with the pulses
          pulses.pause()

          # Print the pulses. pulses[0] is an active pulse unless the length
          # reached max length and idle pulses are recorded.
          print(pulses)

          # Clear the rest
          pulses.clear()

          # Resume with an 80 microsecond active pulse
          pulses.resume(80)"""
        ...

    def deinit(self) -> None:
        """Deinitialises the PulseIn and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> PulseIn:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def pause(self) -> None:
        """Pause pulse capture"""
        ...

    def resume(self, trigger_duration: int = 0) -> None:
        """Resumes pulse capture after an optional trigger pulse.

        .. warning:: Using trigger pulse with a device that drives both high and
          low signals risks a short. Make sure your device is open drain (only
          drives low) when using a trigger pulse. You most likely added a
          "pull-up" resistor to your circuit to do this.

        :param int trigger_duration: trigger pulse duration in microseconds"""
        ...

    def clear(self) -> None:
        """Clears all captured pulses"""
        ...

    def popleft(self) -> int:
        """Removes and returns the oldest read pulse duration in microseconds."""
        ...
    maxlen: int
    """The maximum length of the PulseIn. When len() is equal to maxlen,
    it is unclear which pulses are active and which are idle."""
    paused: bool
    """True when pulse capture is paused as a result of :py:func:`pause` or an error during capture
    such as a signal that is too fast."""
    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Returns the number of pulse durations currently stored.

        This allows you to::

          pulses = pulseio.PulseIn(pin)
          print(len(pulses))"""
        ...

    def __getitem__(self, index: int) -> Optional[int]:
        """Returns the value at the given index or values in slice.

        This allows you to::

          pulses = pulseio.PulseIn(pin)
          print(pulses[0])"""
        ...

class PulseOut:
    """Pulse PWM-modulated "carrier" output on and off. This is commonly used in infrared remotes. The
    pulsed signal consists of timed on and off periods. Unlike `pwmio.PWMOut`, there is no set duration
    for on and off pairs."""

    def __init__(
        self,
        pin: microcontroller.Pin,
        *,
        frequency: int = 38000,
        duty_cycle: int = 1 << 15,
    ) -> None:
        """Create a PulseOut object associated with the given pin.

        :param ~microcontroller.Pin pin: Signal output pin
        :param int frequency: Carrier signal frequency in Hertz
        :param int duty_cycle: 16-bit duty cycle of carrier frequency (0 - 65536)

        Send a short series of pulses::

          import array
          import pulseio
          import board

          # 50% duty cycle at 38kHz.
          pulse = pulseio.PulseOut(board.LED, frequency=38000, duty_cycle=32768)
          #                             on   off     on    off    on
          pulses = array.array('H', [65000, 1000, 65000, 65000, 1000])
          pulse.send(pulses)

          # Modify the array of pulses.
          pulses[0] = 200
          pulse.send(pulses)"""
        ...

    def deinit(self) -> None:
        """Deinitialises the PulseOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> PulseOut:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def send(self, pulses: ReadableBuffer) -> None:
        """Pulse alternating on and off durations in microseconds starting with on.
        ``pulses`` must be an `array.array` with data type 'H' for unsigned
        halfword (two bytes).

        This method waits until the whole array of pulses has been sent and
        ensures the signal is off afterwards.

        :param array.array pulses: pulse durations in microseconds"""
        ...
