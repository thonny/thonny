"""Support for pulse based protocols

The `pulseio` module contains classes to provide access to basic pulse IO.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import pulseio
  import time
  from board import *

  pwm = pulseio.PWMOut(D13)
  pwm.duty_cycle = 2 ** 15
  time.sleep(0.1)

This example will initialize the the device, set
:py:data:`~pulseio.PWMOut.duty_cycle`, and then sleep 0.1 seconds.
CircuitPython will automatically turn off the PWM when it resets all
hardware after program completion. Use ``deinit()`` or a ``with`` statement
to do it yourself."""

class PWMOut:
    """Output a Pulse Width Modulated signal on a given pin."""

    def __init__(self, pin: microcontroller.Pin, *, duty_cycle: int = 0, frequency: int = 500, variable_frequency: bool = False):
        """Create a PWM object associated with the given pin. This allows you to
        write PWM signals out on the given pin. Frequency is fixed after init
        unless ``variable_frequency`` is True.

        .. note:: When ``variable_frequency`` is True, further PWM outputs may be
          limited because it may take more internal resources to be flexible. So,
          when outputting both fixed and flexible frequency signals construct the
          fixed outputs first.

        :param ~microcontroller.Pin pin: The pin to output to
        :param int duty_cycle: The fraction of each pulse which is high. 16-bit
        :param int frequency: The target frequency in Hertz (32-bit)
        :param bool variable_frequency: True if the frequency will change over time

        Simple LED fade::

          import pulseio
          import board

          pwm = pulseio.PWMOut(board.D13)     # output on D13
          pwm.duty_cycle = 2 ** 15            # Cycles the pin with 50% duty cycle (half of 2 ** 16) at the default 500hz

        PWM at specific frequency (servos and motors)::

          import pulseio
          import board

          pwm = pulseio.PWMOut(board.D13, frequency=50)
          pwm.duty_cycle = 2 ** 15                  # Cycles the pin with 50% duty cycle (half of 2 ** 16) at 50hz

        Variable frequency (usually tones)::

          import pulseio
          import board
          import time

          pwm = pulseio.PWMOut(board.D13, duty_cycle=2 ** 15, frequency=440, variable_frequency=True)
          time.sleep(0.2)
          pwm.frequency = 880
          time.sleep(0.1)"""
        ...

    def deinit(self, ) -> Any:
        """Deinitialises the PWMOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    duty_cycle: Any = ...
    """16 bit value that dictates how much of one cycle is high (1) versus low
    (0). 0xffff will always be high, 0 will always be low and 0x7fff will
    be half high and then half low.

    Depending on how PWM is implemented on a specific board, the internal
    representation for duty cycle might have less than 16 bits of resolution.
    Reading this property will return the value from the internal representation,
    so it may differ from the value set."""

    frequency: Any = ...
    """32 bit value that dictates the PWM frequency in Hertz (cycles per
    second). Only writeable when constructed with ``variable_frequency=True``.

    Depending on how PWM is implemented on a specific board, the internal value
    for the PWM's duty cycle may need to be recalculated when the frequency
    changes. In these cases, the duty cycle is automatically recalculated
    from the original duty cycle value. This should happen without any need
    to manually re-set the duty cycle."""

class PulseIn:
    """Measure a series of active and idle pulses. This is commonly used in infrared receivers
       and low cost temperature sensors (DHT). The pulsed signal consists of timed active and
       idle periods. Unlike PWM, there is no set duration for active and idle pairs."""

    def __init__(self, pin: microcontroller.Pin, maxlen: int = 2, *, idle_state: bool = False):
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

    def deinit(self, ) -> Any:
        """Deinitialises the PulseIn and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def pause(self, ) -> Any:
        """Pause pulse capture"""
        ...

    def resume(self, trigger_duration: int = 0) -> Any:
        """Resumes pulse capture after an optional trigger pulse.

        .. warning:: Using trigger pulse with a device that drives both high and
          low signals risks a short. Make sure your device is open drain (only
          drives low) when using a trigger pulse. You most likely added a
          "pull-up" resistor to your circuit to do this.

        :param int trigger_duration: trigger pulse duration in microseconds"""
        ...

    def clear(self, ) -> Any:
        """Clears all captured pulses"""
        ...

    def popleft(self, ) -> Any:
        """Removes and returns the oldest read pulse."""
        ...

    maxlen: Any = ...
    """The maximum length of the PulseIn. When len() is equal to maxlen,
    it is unclear which pulses are active and which are idle."""

    paused: Any = ...
    """True when pulse capture is paused as a result of :py:func:`pause` or an error during capture
    such as a signal that is too fast."""

    def __len__(self, ) -> Any:
        """Returns the current pulse length

        This allows you to::

          pulses = pulseio.PulseIn(pin)
          print(len(pulses))"""
        ...

    def __getitem__(self, index: Any) -> Any:
        """Returns the value at the given index or values in slice.

        This allows you to::

          pulses = pulseio.PulseIn(pin)
          print(pulses[0])"""
        ...

class PulseOut:
    """Pulse PWM "carrier" output on and off. This is commonly used in infrared remotes. The
       pulsed signal consists of timed on and off periods. Unlike PWM, there is no set duration
       for on and off pairs."""

    def __init__(self, carrier: pulseio.PWMOut):
        """Create a PulseOut object associated with the given PWMout object.

        :param ~pulseio.PWMOut carrier: PWMOut that is set to output on the desired pin.

        Send a short series of pulses::

          import array
          import pulseio
          import board

          # 50% duty cycle at 38kHz.
          pwm = pulseio.PWMOut(board.D13, frequency=38000, duty_cycle=32768)
          pulse = pulseio.PulseOut(pwm)
          #                             on   off     on    off    on
          pulses = array.array('H', [65000, 1000, 65000, 65000, 1000])
          pulse.send(pulses)

          # Modify the array of pulses.
          pulses[0] = 200
          pulse.send(pulses)"""
        ...

    def deinit(self, ) -> Any:
        """Deinitialises the PulseOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def send(self, pulses: array.array) -> Any:
        """Pulse alternating on and off durations in microseconds starting with on.
        ``pulses`` must be an `array.array` with data type 'H' for unsigned
        halfword (two bytes).

        This method waits until the whole array of pulses has been sent and
        ensures the signal is off afterwards.

        :param array.array pulses: pulse durations in microseconds"""
        ...

