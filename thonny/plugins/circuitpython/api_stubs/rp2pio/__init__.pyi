"""Hardware interface to RP2 series' programmable IO (PIO) peripheral."""

from __future__ import annotations

from typing import List, Optional

import microcontroller
from circuitpython_typing import ReadableBuffer, WriteableBuffer

def pins_are_sequential(pins: List[microcontroller.Pin]) -> bool:
    """Return True if the pins have sequential GPIO numbers, False otherwise"""
    ...

class StateMachine:
    """A single PIO StateMachine

    The programmable I/O peripheral on the RP2 series of microcontrollers is
    unique. It is a collection of generic state machines that can be
    used for a variety of protocols. State machines may be independent or
    coordinated. Program memory and IRQs are shared between the state machines
    in a particular PIO instance. They are independent otherwise.

    This class is designed to facilitate sharing of PIO resources. By default,
    it is assumed that the state machine is used on its own and can be placed
    in either PIO. State machines with the same program will be placed in the
    same PIO if possible."""

    def __init__(
        self,
        program: ReadableBuffer,
        frequency: int,
        *,
        init: Optional[ReadableBuffer] = None,
        first_out_pin: Optional[microcontroller.Pin] = None,
        out_pin_count: int = 1,
        initial_out_pin_state: int = 0,
        initial_out_pin_direction: int = 0xFFFFFFFF,
        first_in_pin: Optional[microcontroller.Pin] = None,
        in_pin_count: int = 1,
        pull_in_pin_up: int = 0,
        pull_in_pin_down: int = 0,
        first_set_pin: Optional[microcontroller.Pin] = None,
        set_pin_count: int = 1,
        initial_set_pin_state: int = 0,
        initial_set_pin_direction: int = 0x1F,
        first_sideset_pin: Optional[microcontroller.Pin] = None,
        sideset_pin_count: int = 1,
        initial_sideset_pin_state: int = 0,
        initial_sideset_pin_direction: int = 0x1F,
        sideset_enable: bool = False,
        exclusive_pin_use: bool = True,
        auto_pull: bool = False,
        pull_threshold: int = 32,
        out_shift_right: bool = True,
        wait_for_txstall: bool = True,
        auto_push: bool = False,
        push_threshold: int = 32,
        in_shift_right: bool = True,
        user_interruptible: bool = True,
    ) -> None:

        """Construct a StateMachine object on the given pins with the given program.

        :param ReadableBuffer program: the program to run with the state machine
        :param int frequency: the target clock frequency of the state machine. Actual may be less.
        :param ReadableBuffer init: a program to run once at start up. This is run after program
             is started so instructions may be intermingled
        :param ~microcontroller.Pin first_out_pin: the first pin to use with the OUT instruction
        :param int out_pin_count: the count of consecutive pins to use with OUT starting at first_out_pin
        :param int initial_out_pin_state: the initial output value for out pins starting at first_out_pin
        :param int initial_out_pin_direction: the initial output direction for out pins starting at first_out_pin
        :param ~microcontroller.Pin first_in_pin: the first pin to use with the IN instruction
        :param int in_pin_count: the count of consecutive pins to use with IN starting at first_in_pin
        :param int pull_in_pin_up: a 1-bit in this mask sets pull up on the corresponding in pin
        :param int pull_in_pin_down: a 1-bit in this mask sets pull down on the corresponding in pin. Setting both pulls enables a "bus keep" function, i.e. a weak pull to whatever is current high/low state of GPIO.
        :param ~microcontroller.Pin first_set_pin: the first pin to use with the SET instruction
        :param int set_pin_count: the count of consecutive pins to use with SET starting at first_set_pin
        :param int initial_set_pin_state: the initial output value for set pins starting at first_set_pin
        :param int initial_set_pin_direction: the initial output direction for set pins starting at first_set_pin
        :param ~microcontroller.Pin first_sideset_pin: the first pin to use with a side set
        :param int sideset_pin_count: the count of consecutive pins to use with a side set starting at first_sideset_pin. Does not include sideset enable
        :param int initial_sideset_pin_state: the initial output value for sideset pins starting at first_sideset_pin
        :param int initial_sideset_pin_direction: the initial output direction for sideset pins starting at first_sideset_pin
        :param bool sideset_enable: True when the top sideset bit is to enable. This should be used with the ".side_set # opt" directive
        :param ~microcontroller.Pin jmp_pin: the pin which determines the branch taken by JMP PIN instructions
        :param bool exclusive_pin_use: When True, do not share any pins with other state machines. Pins are never shared with other peripherals
        :param bool auto_pull: When True, automatically load data from the tx FIFO into the
            output shift register (OSR) when an OUT instruction shifts more than pull_threshold bits
        :param int pull_threshold: Number of bits to shift before loading a new value into the OSR from the tx FIFO
        :param bool out_shift_right: When True, data is shifted out the right side (LSB) of the
            OSR. It is shifted out the left (MSB) otherwise. NOTE! This impacts data alignment
            when the number of bytes is not a power of two (1, 2 or 4 bytes).
        :param bool wait_for_txstall: When True, writing data out will block until the TX FIFO and OSR are empty
            and an instruction is stalled waiting for more data. When False, data writes won't
            wait for the OSR to empty (only the TX FIFO) so make sure you give enough time before
            deiniting or stopping the state machine.
        :param bool auto_push: When True, automatically save data from input shift register
             (ISR) into the rx FIFO when an IN instruction shifts more than push_threshold bits
        :param int push_threshold: Number of bits to shift before saving the ISR value to the RX FIFO
        :param bool in_shift_right: When True, data is shifted into the right side (LSB) of the
            ISR. It is shifted into the left (MSB) otherwise. NOTE! This impacts data alignment
            when the number of bytes is not a power of two (1, 2 or 4 bytes).
        :param bool user_interruptible: When True (the default),
            `write()`, `readinto()`, and `write_readinto()` can be interrupted by a ctrl-C.
            This is useful when developing a PIO program: if there is an error in the program
            that causes an infinite loop, you will be able to interrupt the loop.
            However, if you are writing to a device that can get into a bad state if a read or write
            is interrupted, you may want to set this to False after your program has been vetted.
        """
        ...
    def deinit(self) -> None:
        """Turn off the state machine and release its resources."""
        ...
    def __enter__(self) -> StateMachine:
        """No-op used by Context Managers.
        Provided by context manager helper."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def restart(self) -> None:
        """Resets this state machine, runs any init and enables the clock."""
        ...
    def run(self, instructions: ReadableBuffer) -> None:
        """Runs all given instructions. They will likely be interleaved with
        in-memory instructions. Make sure this doesn't wait for input!

        This can be used to output internal state to the RX FIFO and then
        read with `readinto`."""
        ...
    def stop(self) -> None:
        """Stops the state machine clock. Use `restart` to enable it."""
        ...
    def write(
        self, buffer: ReadableBuffer, *, start: int = 0, end: Optional[int] = None
    ) -> None:
        """Write the data contained in ``buffer`` to the state machine. If the buffer is empty, nothing happens.

        Writes to the FIFO will match the input buffer's element size. For example, bytearray elements
        will perform 8 bit writes to the PIO FIFO. The RP2040's memory bus will duplicate the value into
        the other byte positions. So, pulling more data in the PIO assembly will read the duplicated values.

        To perform 16 or 32 bits writes into the FIFO use an `array.array` with a type code of the desired
        size.

        :param ~circuitpython_typing.ReadableBuffer buffer: Write out the data in this buffer
        :param int start: Start of the slice of ``buffer`` to write out: ``buffer[start:end]``
        :param int end: End of the slice; this index is not included. Defaults to ``len(buffer)``"""
        ...
    def readinto(
        self, buffer: WriteableBuffer, *, start: int = 0, end: Optional[int] = None
    ) -> None:
        """Read into ``buffer``. If the number of bytes to read is 0, nothing happens. The buffer
        includes any data added to the fifo even if it was added before this was called.

        Reads from the FIFO will match the input buffer's element size. For example, bytearray elements
        will perform 8 bit reads from the PIO FIFO. The alignment within the 32 bit value depends on
        ``in_shift_right``. When ``in_shift_right`` is True, the upper N bits will be read. The lower
        bits will be read when ``in_shift_right`` is False.

        To perform 16 or 32 bits writes into the FIFO use an `array.array` with a type code of the desired
        size.

        :param ~circuitpython_typing.WriteableBuffer buffer: Read data into this buffer
        :param int start: Start of the slice of ``buffer`` to read into: ``buffer[start:end]``
        :param int end: End of the slice; this index is not included. Defaults to ``len(buffer)``"""
        ...
    def write_readinto(
        self,
        buffer_out: ReadableBuffer,
        buffer_in: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: Optional[int] = None,
        in_start: int = 0,
        in_end: Optional[int] = None,
    ) -> None:
        """Write out the data in ``buffer_out`` while simultaneously reading data into ``buffer_in``.
        The lengths of the slices defined by ``buffer_out[out_start:out_end]`` and ``buffer_in[in_start:in_end]``
        may be different. The function will return once both are filled.
        If buffer slice lengths are both 0, nothing happens.

        Data transfers to and from the FIFOs will match the corresponding buffer's element size. See
        `write` and `readinto` for details.

        To perform 16 or 32 bits writes into the FIFO use an `array.array` with a type code of the desired
        size.

        :param ~circuitpython_typing.ReadableBuffer buffer_out: Write out the data in this buffer
        :param ~circuitpython_typing.WriteableBuffer buffer_in: Read data into this buffer
        :param int out_start: Start of the slice of buffer_out to write out: ``buffer_out[out_start:out_end]``
        :param int out_end: End of the slice; this index is not included. Defaults to ``len(buffer_out)``
        :param int in_start: Start of the slice of ``buffer_in`` to read into: ``buffer_in[in_start:in_end]``
        :param int in_end: End of the slice; this index is not included. Defaults to ``len(buffer_in)``"""
        ...
    def clear_rxfifo(self) -> None:
        """Clears any unread bytes in the rxfifo."""
        ...
    frequency: int
    """The actual state machine frequency. This may not match the frequency requested
    due to internal limitations."""

    rxstall: bool
    """True when the state machine has stalled due to a full RX FIFO since the last
       `clear_rxfifo` call."""

    in_waiting: int
    """The number of words available to readinto"""
