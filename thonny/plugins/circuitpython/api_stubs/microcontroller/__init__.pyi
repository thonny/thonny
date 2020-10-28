"""Pin references and cpu functionality

The `microcontroller` module defines the pins from the perspective of the
microcontroller. See `board` for board-specific pin mappings."""

cpu: Processor = ...
"""CPU information and control, such as ``cpu.temperature`` and ``cpu.frequency``
(clock frequency).
This object is the sole instance of `microcontroller.Processor`."""

def delay_us(delay: Any) -> Any:
    """Dedicated delay method used for very short delays. **Do not** do long delays
    because this stops all other functions from completing. Think of this as an empty
    ``while`` loop that runs for the specified ``(delay)`` time. If you have other
    code or peripherals (e.g audio recording) that require specific timing or
    processing while you are waiting, explore a different avenue such as using
    `time.sleep()`."""
    ...

def disable_interrupts() -> Any:
    """Disable all interrupts. Be very careful, this can stall everything."""
    ...

def enable_interrupts() -> Any:
    """Enable the interrupts that were enabled at the last disable."""
    ...

def on_next_reset(run_mode: microcontroller.RunMode) -> Any:
    """Configure the run mode used the next time the microcontroller is reset but
    not powered down.

    :param ~microcontroller.RunMode run_mode: The next run mode"""
    ...

def reset() -> Any:
    """Reset the microcontroller. After reset, the microcontroller will enter the
    run mode last set by `on_next_reset`.

    .. warning:: This may result in file system corruption when connected to a
      host computer. Be very careful when calling this! Make sure the device
      "Safely removed" on Windows or "ejected" on Mac OSX and Linux."""
    ...

nvm: Any = ...
"""Available non-volatile memory.
This object is the sole instance of `nvm.ByteArray` when available or ``None`` otherwise.

:type: nvm.ByteArray or None"""

""":mod:`microcontroller.pin` --- Microcontroller pin names
--------------------------------------------------------

.. module:: microcontroller.pin
  :synopsis: Microcontroller pin names
  :platform: SAMD21

References to pins as named by the microcontroller"""

class Pin:
    """Identifies an IO pin on the microcontroller."""

    def __init__(self, ):
        """Identifies an IO pin on the microcontroller. They are fixed by the
        hardware so they cannot be constructed on demand. Instead, use
        `board` or `microcontroller.pin` to reference the desired pin."""
        ...

class Processor:
    """Microcontroller CPU information and control

    Usage::

       import microcontroller
       print(microcontroller.cpu.frequency)
       print(microcontroller.cpu.temperature)"""

    def __init__(self, ):
        """You cannot create an instance of `microcontroller.Processor`.
        Use `microcontroller.cpu` to access the sole instance available."""
        ...

    frequency: int = ...
    """The CPU operating frequency in Hertz. (read-only)"""

    temperature: Any = ...
    """The on-chip temperature, in Celsius, as a float. (read-only)

    Is `None` if the temperature is not available."""

    uid: Any = ...
    """The unique id (aka serial number) of the chip as a `bytearray`. (read-only)"""

    voltage: Any = ...
    """The input voltage to the microcontroller, as a float. (read-only)

    Is `None` if the voltage is not available."""

class RunMode:
    """run state of the microcontroller"""

    def __init__(self, ):
        """Enum-like class to define the run mode of the microcontroller and
        CircuitPython."""

    NORMAL: Any = ...
    """Run CircuitPython as normal.

    :type microcontroller.RunMode:"""

    SAFE_MODE: Any = ...
    """Run CircuitPython in safe mode. User code will not be run and the
    file system will be writeable over USB.

    :type microcontroller.RunMode:"""

    BOOTLOADER: Any = ...
    """Run the bootloader.

    :type microcontroller.RunMode:"""

