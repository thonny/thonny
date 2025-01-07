"""Low-level utilities.
"""
from typing import Any
from .microbit import MicroBitDigitalPin

def unique_id() -> bytes:
    """Get a byte string with a unique identifier of a board.

    Example: ``machine.unique_id()``

    :return: An identifier that varies from one board instance to another.
    """
    ...

def reset() -> None:
    """Reset the device in a manner similar to pushing the external RESET button.

    Example: ``machine.reset()``
    """
    ...

def freq() -> int:
    """Get the CPU frequency in hertz.

    Example: ``machine.freq()``

    :return: The CPU frequency.
    """
    ...

def disable_irq() -> Any:
    """Disable interrupt requests.

    Example: ``interrupt_state = machine.disable_irq()``

    :return: the previous IRQ state which should be considered an opaque value

    The return value should be passed to the ``enable_irq`` function to restore
    interrupts to their original state.
    """
    ...

def enable_irq(state: Any) -> None:
    """Re-enable interrupt requests.

    Example: ``machine.enable_irq(interrupt_state)``

    :param state: The value that was returned from the most recent call to the ``disable_irq`` function.
    """
    ...

def time_pulse_us(
    pin: MicroBitDigitalPin, pulse_level: int, timeout_us: int = 1000000
) -> int:
    """Time a pulse on a pin.

    Example: ``time_pulse_us(pin0, 1)``

    If the current input value of the pin is different to ``pulse_level``, the
    function first waits until the pin input becomes equal to
    ``pulse_level``, then times the duration that the pin is equal to
    ``pulse_level``. If the pin is already equal to ``pulse_level`` then timing
    starts straight away.

    :param pin: The pin to use
    :param pulse_level: 0 to time a low pulse or 1 to time a high pulse
    :param timeout_us: A microsecond timeout
    :return: The duration of the pulse in microseconds, or -1 for a timeout waiting for the level to match ``pulse_level``, or -2 on timeout waiting for the pulse to end
    """
    ...

class mem:
    """The class for the ``mem8``, ``mem16`` and ``mem32`` memory views."""

    def __getitem__(self, address: int) -> int:
        """Access a value from memory.

        :param address: The memory address.
        :return: The value at that address as an integer.
        """
        ...
    def __setitem__(self, address: int, value: int) -> None:
        """Set a value at the given address.

        :param address: The memory address.
        :param value: The integer value to set.
        """
        ...

mem8: mem
"""8-bit (byte) view of memory."""

mem16: mem
"""16-bit view of memory."""

mem32: mem
"""32-bit view of memory."""
