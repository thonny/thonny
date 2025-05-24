"""Hardware interface to RP2 series' programmable IO (PIO) peripheral.

.. note:: This module is intended to be used with the `adafruit_pioasm library
    <https://github.com/adafruit/Adafruit_CircuitPython_PIOASM>`_.  For an
    introduction and guide to working with PIO in CircuitPython, see `this
    Learn guide <https://learn.adafruit.com/intro-to-rp2040-pio-with-circuitpython>`_.

.. warning:: Using PIO inputs on Raspberry Pi RP2350 A2 stepping has some limitations
   due to a GPIO hardware issue that causes excessive leakage current (~120uA).
   A pin can read as high even when driven or pulled low, if the input signal is high
   impedance or if an attached pull-down resistor is too weak (has too high a value).
   See the warning in `digitalio` for more information.
"""

from __future__ import annotations

import array
from typing import List, Literal, Optional

import digitalio
import memorymap
import microcontroller
from circuitpython_typing import ReadableBuffer, WriteableBuffer

def pins_are_sequential(pins: List[microcontroller.Pin]) -> bool:
    """Return True if the pins have sequential GPIO numbers, False otherwise"""
    ...

import memorymap

FifoType = Literal["auto", "txrx", "tx", "rx", "txput", "txget", "putget"]
"""A type representing one of the strings ``"auto"``, ``"txrx"``, ``"tx"``, ``"rx"``, ``"txput"``, ``"txget"`` or ``"putget"``. These values are supported on RP2350. For type-checking only, not actually defined in CircuitPython."""
FifoType_piov0 = Literal["auto", "txrx", "tx", "rx"]
"""A type representing one of the strings ``"auto"``, ``"txrx"``, ``"tx"``, or ``"rx"``. These values are supported on both RP2350 and RP2040. For type-checking only, not actually defined in CircuitPython."""
MovStatusType = Literal["txfifo", "rxfifo", "irq"]
"""A type representing one of the strings ``"txfifo"``, ``"rxfifo"``, or ``"irq"``. These values are supported on RP2350. For type-checking only, not actually defined in CircuitPython."""
MovStatusType_piov0 = Literal["txfifo"]
"""A type representing the string ``"txfifo"``. This value is supported on RP2350 and RP2040. For type-checking only, not actually defined in CircuitPython."""

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
        pio_version: int = 0,
        may_exec: Optional[ReadableBuffer] = None,
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
        sideset_pindirs: bool = False,
        initial_sideset_pin_state: int = 0,
        initial_sideset_pin_direction: int = 0x1F,
        sideset_enable: bool = False,
        jmp_pin: Optional[microcontroller.Pin] = None,
        jmp_pin_pull: Optional[digitalio.Pull] = None,
        exclusive_pin_use: bool = True,
        auto_pull: bool = False,
        pull_threshold: int = 32,
        out_shift_right: bool = True,
        wait_for_txstall: bool = True,
        auto_push: bool = False,
        push_threshold: int = 32,
        in_shift_right: bool = True,
        user_interruptible: bool = True,
        wrap_target: int = 0,
        wrap: int = -1,
        offset: int = -1,
        fifo_type: FifoType = "auto",
        mov_status_type: MovStatusType = "txfifo",
        mov_status_n: int = 0,
    ) -> None:
        """Construct a StateMachine object on the given pins with the given program.

        The following parameters are usually supplied directly:

        :param ReadableBuffer program: the program to run with the state machine
        :param int frequency: the target clock frequency of the state machine. Actual may be less. Use 0 for system clock speed.
        :param ReadableBuffer init: a program to run once at start up. This is run after program
             is started so instructions may be intermingled
        :param ReadableBuffer may_exec: Instructions that may be executed via `StateMachine.run` calls.
            Some elements of the `StateMachine`'s configuration are inferred from the instructions used;
            for instance, if there is no ``in`` or ``push`` instruction, then the `StateMachine` is configured without a receive FIFO.
            In this case, passing a ``may_exec`` program containing an ``in`` instruction such as ``in x``, a receive FIFO will be configured.
        :param ~microcontroller.Pin first_out_pin: the first pin to use with the OUT instruction
        :param int initial_out_pin_state: the initial output value for out pins starting at first_out_pin
        :param int initial_out_pin_direction: the initial output direction for out pins starting at first_out_pin
        :param ~microcontroller.Pin first_in_pin: the first pin to use with the IN instruction
        :param int pull_in_pin_up: a 1-bit in this mask sets pull up on the corresponding in pin
        :param int pull_in_pin_down: a 1-bit in this mask sets pull down on the corresponding in pin. Setting both pulls enables a "bus keep" function, i.e. a weak pull to whatever is current high/low state of GPIO.
        :param ~microcontroller.Pin first_set_pin: the first pin to use with the SET instruction
        :param int initial_set_pin_state: the initial output value for set pins starting at first_set_pin
        :param int initial_set_pin_direction: the initial output direction for set pins starting at first_set_pin
        :param ~microcontroller.Pin first_sideset_pin: the first pin to use with a side set
        :param int initial_sideset_pin_state: the initial output value for sideset pins starting at first_sideset_pin
        :param int initial_sideset_pin_direction: the initial output direction for sideset pins starting at first_sideset_pin
        :param bool sideset_enable: True when the top sideset bit is to enable. This should be used with the ".side_set # opt" directive
        :param ~microcontroller.Pin jmp_pin: the pin which determines the branch taken by JMP PIN instructions
        :param ~digitalio.Pull jmp_pin_pull: The pull value for the jmp pin, default is no pull.
        :param bool exclusive_pin_use: When True, do not share any pins with other state machines. Pins are never shared with other peripherals
        :param bool wait_for_txstall: When True, writing data out will block until the TX FIFO and OSR are empty
            and an instruction is stalled waiting for more data. When False, data writes won't
            wait for the OSR to empty (only the TX FIFO) so make sure you give enough time before
            deiniting or stopping the state machine.
        :param bool user_interruptible: When True (the default),
            `write()`, `readinto()`, and `write_readinto()` can be interrupted by a ctrl-C.
            This is useful when developing a PIO program: if there is an error in the program
            that causes an infinite loop, you will be able to interrupt the loop.
            However, if you are writing to a device that can get into a bad state if a read or write
            is interrupted, you may want to set this to False after your program has been vetted.
        :param int offset: A specific offset in the state machine's program memory where the program must be loaded.
            The default value, -1, allows the program to be loaded at any offset.
            This is appropriate for most programs.

        The following parameters are usually set via assembler directives and passed using a ``**program.pio_kwargs`` argument but may also be specified directly:

        :param int out_pin_count: the count of consecutive pins to use with OUT starting at first_out_pin
        :param int in_pin_count: the count of consecutive pins to use with IN starting at first_in_pin
        :param int set_pin_count: the count of consecutive pins to use with SET starting at first_set_pin
        :param int sideset_pin_count: the count of consecutive pins to use with a side set starting at first_sideset_pin. Does not include sideset enable
        :param bool sideset_pindirs: `True` to indicate that the side set values should be applied to the PINDIRs and not the PINs
        :param int pio_version: The version of the PIO peripheral required by the program. The constructor will raise an error if the actual hardware is not compatible with this program version.
        :param bool auto_push: When True, automatically save data from input shift register
             (ISR) into the rx FIFO when an IN instruction shifts more than push_threshold bits
        :param int push_threshold: Number of bits to shift before saving the ISR value to the RX FIFO
        :param bool in_shift_right: When True, data is shifted into the right side (LSB) of the
            ISR. It is shifted into the left (MSB) otherwise. NOTE! This impacts data alignment
            when the number of bytes is not a power of two (1, 2 or 4 bytes).
        :param bool auto_pull: When True, automatically load data from the tx FIFO into the
            output shift register (OSR) when an OUT instruction shifts more than pull_threshold bits
        :param int pull_threshold: Number of bits to shift before loading a new value into the OSR from the tx FIFO
        :param bool out_shift_right: When True, data is shifted out the right side (LSB) of the
            OSR. It is shifted out the left (MSB) otherwise. NOTE! This impacts data alignment
            when the number of bytes is not a power of two (1, 2 or 4 bytes).
        :param int wrap_target: The target instruction number of automatic wrap. Defaults to the first instruction of the program.
        :param int wrap: The instruction after which to wrap to the ``wrap``
            instruction. As a special case, -1 (the default) indicates the
            last instruction of the program.
        :param FifoType fifo_type: How the program accessess the FIFOs. PIO version 0 in the RP2040 only supports a subset of values, `FifoType_piov0`.
        :param MovStatusType mov_status_type: What condition the ``mov status`` instruction checks. PIO version 0 in the RP2040 only supports a subset of values, `MovStatusType_piov0`.
        :param MovStatusType mov_status_n: The FIFO depth or IRQ the ``mov status`` instruction checks for. For ``mov_status irq`` this includes the encoding of the ``next``/``prev`` selection bits.
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
        self,
        buffer: ReadableBuffer,
        *,
        start: int = 0,
        end: Optional[int] = None,
        swap: bool = False,
    ) -> None:
        """Write the data contained in ``buffer`` to the state machine. If the buffer is empty, nothing happens.

        Writes to the FIFO will match the input buffer's element size. For example, bytearray elements
        will perform 8 bit writes to the PIO FIFO. The RP2040's memory bus will duplicate the value into
        the other byte positions. So, pulling more data in the PIO assembly will read the duplicated values.

        To perform 16 or 32 bits writes into the FIFO use an `array.array` with a type code of the desired
        size.

        :param ~circuitpython_typing.ReadableBuffer buffer: Write out the data in this buffer
        :param int start: Start of the slice of ``buffer`` to write out: ``buffer[start:end]``
        :param int end: End of the slice; this index is not included. Defaults to ``len(buffer)``
        :param bool swap: For 2- and 4-byte elements, swap (reverse) the byte order"""
        ...

    def background_write(
        self,
        once: Optional[ReadableBuffer] = None,
        *,
        loop: Optional[ReadableBuffer] = None,
        loop2: Optional[ReadableBuffer] = None,
        swap: bool = False,
    ) -> None:
        """Write data to the TX fifo in the background, with optional looping.

        First, if any previous ``once`` or ``loop`` buffer has not been started, this function blocks until they have been started.
        This means that any ``once`` or ``loop`` buffer will be written at least once.
        Then the ``once`` and/or ``loop`` buffers are queued. and the function returns.
        The ``once`` buffer (if specified) will be written just once.
        Finally, the ``loop`` and/or ``loop2`` buffer (if specified) will continue being looped indefinitely.  If both ``loop`` and ``loop2`` are specified, they will alternate.

        Writes to the FIFO will match the input buffer's element size. For example, bytearray elements
        will perform 8 bit writes to the PIO FIFO. The RP2040's memory bus will duplicate the value into
        the other byte positions. So, pulling more data in the PIO assembly will read the duplicated values.

        To perform 16 or 32 bits writes into the FIFO use an `array.array` with a type code of the desired
        size, or use `memoryview.cast` to change the interpretation of an
        existing buffer.  To send just part of a larger buffer, slice a `memoryview`
        of it.

        If a buffer is modified while it is being written out, the updated
        values will be used. However, because of interactions between CPU
        writes, DMA and the PIO FIFO are complex, it is difficult to predict
        the result of modifying multiple values. Instead, alternate between
        a pair of buffers.

        Having both a ``once`` and a ``loop`` parameter is to support a special case in PWM generation
        where a change in duty cycle requires a special transitional buffer to be used exactly once. Most
        use cases will probably only use one of ``once`` or ``loop``.

        Having neither ``once`` nor ``loop`` terminates an existing
        background looping write after exactly a whole loop. This is in contrast to
        `stop_background_write`, which interrupts an ongoing DMA operation.

        :param ~Optional[circuitpython_typing.ReadableBuffer] once: Data to be written once
        :param ~Optional[circuitpython_typing.ReadableBuffer] loop: Data to be written repeatedly
        :param ~Optional[circuitpython_typing.ReadableBuffer] loop2: Data to be written repeatedly
        :param bool swap: For 2- and 4-byte elements, swap (reverse) the byte order
        """
        ...

    def stop_background_write(self) -> None:
        """Immediately stop a background write, if one is in progress.  Any
        DMA in progress is halted, but items already in the TX FIFO are not
        affected."""
    writing: bool
    """Returns True if a background write is in progress"""
    pending_write: int
    pending: int
    """Returns the number of pending buffers for background writing.

    If the number is 0, then a `StateMachine.background_write` call will not block.
    Note that `pending` is a deprecated alias for `pending_write` and will be removed
    in a future version of CircuitPython."""

    def background_read(
        self,
        once: Optional[WriteableBuffer] = None,
        *,
        loop: Optional[WriteableBuffer] = None,
        loop2: Optional[WriteableBuffer] = None,
        swap: bool = False,
    ) -> None:
        """Read data from the RX fifo in the background, with optional looping.

        First, if any previous ``once`` or ``loop`` buffer has not been started, this function blocks until they have been started.
        This means that any ``once`` or ``loop`` buffer will be read at least once.
        Then the ``once`` and/or ``loop`` buffers are queued. and the function returns.
        The ``once`` buffer (if specified) will be read just once.
        Finally, the ``loop`` and/or ``loop2`` buffer (if specified) will continue being read indefinitely.  If both ``loop`` and ``loop2`` are specified, they will alternate.

        Reads from the FIFO will match the input buffer's element size. For example, bytearray elements
        will perform 8 bit reads from the PIO FIFO. The RP2040's memory bus will duplicate the value into
        the other byte positions. So, pulling more data in the PIO assembly will read the duplicated values.

        To perform 16 or 32 bits reads from the FIFO use an `array.array` with a type code of the desired
        size, or use `memoryview.cast` to change the interpretation of an
        existing buffer.  To receive just part of a larger buffer, slice a `memoryview`
        of it.

        Most use cases will probably only use one of ``once`` or ``loop``.

        Having neither ``once`` nor ``loop`` terminates an existing
        background looping read after exactly a whole loop. This is in contrast to
        `stop_background_read`, which interrupts an ongoing DMA operation.

        :param ~Optional[circuitpython_typing.WriteableBuffer] once: Data to be read once
        :param ~Optional[circuitpython_typing.WriteableBuffer] loop: Data to be read repeatedly
        :param ~Optional[circuitpython_typing.WriteableBuffer] loop2: Data to be read repeatedly
        :param bool swap: For 2- and 4-byte elements, swap (reverse) the byte order
        """
        ...

    def stop_background_read(self) -> None:
        """Immediately stop a background read, if one is in progress.  Any
        DMA in progress is halted, but items already in the RX FIFO are not
        affected."""
    reading: bool
    """Returns True if a background read is in progress"""
    pending_read: int
    """Returns the number of pending buffers for background reading.

    If the number is 0, then a `StateMachine.background_read` call will not block."""

    def readinto(
        self,
        buffer: WriteableBuffer,
        *,
        start: int = 0,
        end: Optional[int] = None,
        swap: bool = False,
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
        :param int end: End of the slice; this index is not included. Defaults to ``len(buffer)``
        :param bool swap: For 2- and 4-byte elements, swap (reverse) the byte order"""
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
        :param int in_end: End of the slice; this index is not included. Defaults to ``len(buffer_in)``
        :param bool swap_out: For 2- and 4-byte elements, swap (reverse) the byte order for the buffer being transmitted (written)
        :param bool swap_in: For 2- and 4-rx elements, swap (reverse) the byte order for the buffer being received (read)
        """
        ...

    def clear_rxfifo(self) -> None:
        """Clears any unread bytes in the rxfifo."""
        ...

    def clear_txstall(self) -> None:
        """Clears the txstall flag."""
        ...
    frequency: int
    """The actual state machine frequency. This may not match the frequency requested
    due to internal limitations."""
    txstall: bool
    """True when the state machine has stalled due to a full TX FIFO since the last
       `clear_txstall` call."""
    rxstall: bool
    """True when the state machine has stalled due to a full RX FIFO since the last
       `clear_rxfifo` call."""
    in_waiting: int
    """The number of words available to readinto"""

    offset: int
    """The instruction offset where the program was actually loaded"""

    pc: int
    """The current program counter of the state machine"""

    rxfifo: memorymap.AddressRange
    """Access the state machine's rxfifo directly

    If the state machine's fifo mode is ``txput`` then accessing this object
    reads values stored by the ``mov rxfifo[], isr`` PIO instruction, and the
    result of modifying it is undefined.

    If the state machine's fifo mode is ``txget`` then modifying this object
    writes values accessed by the ``mov osr, rxfifo[]`` PIO instruction, and
    the result of accessing it is undefined.

    If this state machine's mode is something else, then the property's value is `None`.

    Note: Since the ``txput`` and ``txget`` fifo mode does not exist on RP2040, this property will always be `None`."""

    last_read: array.array
    """Returns the buffer most recently filled by background reads.

    This property is self-clearing -- once read, subsequent reads
    will return a zero-length buffer until the background read buffer
    changes or restarts.
    """
    last_write: array.array
    """Returns the buffer most recently emptied by background writes.

    This property is self-clearing -- once read, subsequent reads
    will return a zero-length buffer until the background write buffer
    changes or restarts.
    """
