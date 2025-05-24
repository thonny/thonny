"""ESP Ultra Low Power Processor Module

The `espulp` module adds ability to load and run
programs on the ESP32-Sx's ultra-low-power RISC-V processor.

.. code-block:: python

    import espulp
    import memorymap

    shared_mem = memorymap.AddressRange(start=0x50000000, length=1024)
    ulp = espulp.ULP()

    with open("program.bin", "rb") as f:
        program = f.read()

    ulp.run(program)
    print(shared_mem[0])
    # ulp.halt()
"""

from __future__ import annotations

from typing import Optional, Sequence

import microcontroller
from circuitpython_typing import ReadableBuffer

...

def get_rtc_gpio_number(pin: microcontroller.Pin) -> Optional[int]:
    """Return the RTC GPIO number of the given pin or None if not connected
    to RTC GPIO."""
    ...

class Architecture:
    """The ULP architectures available."""

    FSM: Architecture
    """The ULP Finite State Machine."""

    RISCV: Architecture
    """The ULP RISC-V Coprocessor."""

class ULP:
    def __init__(self, arch: Architecture = Architecture.FSM) -> None:
        """The ultra-low-power processor.

        Raises an exception if another ULP has been instantiated. This
        ensures that is is only used by one piece of code at a time.

        :param Architecture arch: The ulp arch.
        """
        ...

    def deinit(self) -> None:
        """Deinitialises the ULP and releases it for another program."""
        ...

    def __enter__(self) -> ULP:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def set_wakeup_period(self, period_index: int, period_us: int) -> None:
        """Sets the wakeup period for the ULP.

        :param int period_index: = 0..4. Up to 5 different wakeup periods can be stored
            and used by the wakeup timer.
            By default, the value stored in period index 0 is used.
        :param int period_us: The wakeup period given in microseconds."""
        ...

    def run(
        self,
        program: ReadableBuffer,
        *,
        entrypoint: int = 0,
        pins: Sequence[microcontroller.Pin] = (),
    ) -> None:
        """Loads the program into ULP memory and then runs the program.

        The program will continue to run even Python is halted or in deep-sleep.

        :param ReadableBuffer program: the ULP binary.
        :param int entrypoint: Specifies the offset (in bytes) of the first instruction
           from the start of the program (Only used by FSM ULP).
        :param Sequence[microcontroller.Pin] pins: Pins made available to the ULP.
           The pins are claimed and not reset until `halt()` is called."""
        ...

    def halt(self) -> None:
        """Halts the running program and releases the pins given in `run()`.
        Note: for the FSM ULP, a running ULP program is not actually interrupted.
        Instead, only the wakeup timer is stopped."""
        ...
    arch: Architecture
    """The ulp architecture. (read-only)"""

class ULPAlarm:
    """Trigger an alarm when the ULP requests wake-up."""

    def __init__(self, ulp: ULP) -> None:
        """Create an alarm that will be triggered when the ULP requests wake-up.

        The alarm is not active until it is passed to an `alarm`-enabling function, such as
        `alarm.light_sleep_until_alarms()` or `alarm.exit_and_deep_sleep_until_alarms()`.

        :param ULP ulp: The ulp instance"""
        ...
