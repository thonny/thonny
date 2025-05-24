"""
Functionality specific to the RP2.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/rp2.html

The ``rp2`` module contains functions and classes specific to the RP2040, as
used in the Raspberry Pi Pico.

See the `RP2040 Python datasheet
<https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf>`_
for more information, and `pico-micropython-examples
<https://github.com/raspberrypi/pico-micropython-examples/tree/master/pio>`_
for example code.

---
Module: 'rp2.PIOASMEmit'

---
This module provides type hints for the `rp2.asm_pio` module in the Raspberry Pi Pico Python SDK.
It includes definitions for constants, functions, and directives used in PIO assembly programming.

The module includes docstrings for each function and directive, providing information on their usage and parameters.

Note: This module is intended for use with type checking and does not contain actual implementations of the functions.

For more information on PIO assembly programming and the Raspberry Pi Pico Python SDK, refer to the following documents:
- raspberry-pi-pico-python-sdk.pdf: https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-python-sdk.pdf
- raspberry-pi-pico-c-sdk.pdf: https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-c-sdk.pdf

For a simpler and clearer reference on PIO assembly, you can also visit: https://dernulleffekt.de/doku.php?id=raspberrypipico:pico_pio


rp2.PIO type hints have to be loaded manually. Add the following lines to the top of the file with the PIO assembler code:

```py   
# -----------------------------------------------
# add type hints for the rp2.PIO Instructions
try: 
    from typing_extensions import TYPE_CHECKING # type: ignore
except ImportError:
    TYPE_CHECKING = False
if TYPE_CHECKING:
    from rp2.asm_pio import *
# -----------------------------------------------
```

---
Module: 'rp2' on micropython-v1.25.0-rp2-RPI_PICO2_W
"""

# MCU: {'build': '', 'ver': '1.25.0', 'version': '1.25.0', 'port': 'rp2', 'board': 'RPI_PICO2_W', 'mpy': 'v6.3', 'family': 'micropython', 'cpu': 'RP2350', 'arch': 'armv7emsp'}
# Stubber: v1.24.0
from __future__ import annotations
from typing import Union, Dict, List, Callable, Literal, overload, Any, Optional, Final
from _typeshed import Incomplete
from micropython import const
from typing_extensions import Awaitable, TypeAlias, TypeVar, TYPE_CHECKING
from _mpy_shed import AnyReadableBuf, AnyWritableBuf, _IRQ
from vfs import AbstractBlockDev
from machine import Pin

_PIO_ASM_Program: TypeAlias = Incomplete
_IRQ_TRIGGERS: TypeAlias = Literal[256, 512, 1024, 2048]

_pio_funcs: dict = {}
_pio_directives: tuple = ()
_pio_instructions: tuple = ()

def bootsel_button() -> int:
    """
    Temporarily turns the QSPI_SS pin into an input and reads its value,
    returning 1 for low and 0 for high.
    On a typical RP2040 board with a BOOTSEL button, a return value of 1
    indicates that the button is pressed.

    Since this function temporarily disables access to the external flash
    memory, it also temporarily disables interrupts and the other core to
    prevent them from trying to execute code from flash.
    """
    ...

def asm_pio(
    *,
    out_init: Union[Pin, List[Pin], int, List[int], None] = None,
    set_init: Union[Pin, List[Pin], int, List[int], None] = None,
    sideset_init: Union[Pin, List[Pin], int, List[int], None] = None,
    in_shiftdir=0,
    out_shiftdir=0,
    autopush=False,
    autopull=False,
    push_thresh=32,
    pull_thresh=32,
    fifo_join=PIO.JOIN_NONE,
) -> Callable[..., _PIO_ASM_Program]:
    """
    Assemble a PIO program.

    The following parameters control the initial state of the GPIO pins, as one
    of `PIO.IN_LOW`, `PIO.IN_HIGH`, `PIO.OUT_LOW` or `PIO.OUT_HIGH`. If the
    program uses more than one pin, provide a tuple, e.g.
    ``out_init=(PIO.OUT_LOW, PIO.OUT_LOW)``.

    - *out_init* configures the pins used for ``out()`` instructions.
    - *set_init* configures the pins used for ``set()`` instructions. There can
      be at most 5.
    - *sideset_init* configures the pins used for ``.side()`` modifiers. There
      can be at most 5.
    - *side_pindir* when set to ``True`` configures ``.side()`` modifiers to be
      used for pin directions, instead of pin values (the default, when ``False``).

    The following parameters are used by default, but can be overridden in
    `StateMachine.init()`:

    - *in_shiftdir* is the default direction the ISR will shift, either
      `PIO.SHIFT_LEFT` or `PIO.SHIFT_RIGHT`.
    - *out_shiftdir* is the default direction the OSR will shift, either
      `PIO.SHIFT_LEFT` or `PIO.SHIFT_RIGHT`.
    - *push_thresh* is the threshold in bits before auto-push or conditional
      re-pushing is triggered.
    - *pull_thresh* is the threshold in bits before auto-pull or conditional
      re-pulling is triggered.

    The remaining parameters are:

    - *autopush* configures whether auto-push is enabled.
    - *autopull* configures whether auto-pull is enabled.
    - *fifo_join* configures whether the 4-word TX and RX FIFOs should be
      combined into a single 8-word FIFO for one direction only. The options
      are `PIO.JOIN_NONE`, `PIO.JOIN_RX` and `PIO.JOIN_TX`.
    """
    ...

def country(*args, **kwargs) -> Incomplete: ...
def asm_pio_encode(instr, sideset_count, sideset_opt=False) -> int:
    """
    Assemble a single PIO instruction. You usually want to use `asm_pio()`
    instead.

    >>> rp2.asm_pio_encode("set(0, 1)", 0)
    57345
    """
    ...

def const(*args, **kwargs) -> Incomplete: ...

class DMA:
    """
    Claim one of the DMA controller channels for exclusive use.
    """

    def irq(self, handler=None, hard=False) -> _IRQ:
        """
        Returns the IRQ object for this DMA channel and optionally configures it.
        """
        ...

    def unpack_ctrl(self, value) -> dict:
        """
        Unpack a value for a DMA channel control register into a dictionary with key/value pairs
        for each of the fields in the control register.  *value* is the ``ctrl`` register value
        to unpack.

        This method will return values for all the keys that can be passed to ``DMA.pack_ctrl``.
        In addition, it will also return the read-only flags in the control register: ``busy``,
        which goes high when a transfer starts and low when it ends, and ``ahb_err``, which is
        the logical OR of the ``read_err`` and ``write_err`` flags. These values will be ignored
        when packing, so that the dictionary created by unpacking a control register can be used
        directly as the keyword arguments for packing.
        """
        ...

    def pack_ctrl(self, default=None, **kwargs) -> int:
        """
        Pack the values provided in the keyword arguments into the named fields of a new control
        register value. Any field that is not provided will be set to a default value. The
        default will either be taken from the provided ``default`` value, or if that is not
        given, a default suitable for the current channel; setting this to the current value
        of the `DMA.ctrl` attribute provides an easy way to override a subset of the fields.

        The keys for the keyword arguments can be any key returned by the :meth:`DMA.unpack_ctrl()`
        method. The writable values are:

        - *enable*: ``bool`` Set to enable the channel (default: ``True``).

        - *high_pri*: ``bool`` Make this channel's bus traffic high priority (default: ``False``).

        - *size*: ``int`` Transfer size: 0=byte, 1=half word, 2=word (default: 2).

        - *inc_read*: ``bool`` Increment the read address after each transfer (default: ``True``).

        - *inc_write*: ``bool`` Increment the write address after each transfer (default: ``True``).

        - *ring_size*: ``int`` If non-zero, only the bottom ``ring_size`` bits of one
          address register will change when an address is incremented, causing the
          address to wrap at the next ``1 << ring_size`` byte boundary. Which
          address is wrapped is controlled by the ``ring_sel`` flag. A zero value
          disables address wrapping.

        - *ring_sel*: ``bool`` Set to ``False`` to have the ``ring_size`` apply to the read address
          or ``True`` to apply to the write address.

        - *chain_to*: ``int`` The channel number for a channel to trigger after this transfer
          completes. Setting this value to this DMA object's own channel number
          disables chaining (this is the default).

        - *treq_sel*: ``int`` Select a Transfer Request signal. See section 2.5.3 in the RP2040
          datasheet for details.

        - *irq_quiet*: ``bool`` Do not generate interrupt at the end of each transfer. Interrupts
          will instead be generated when a zero value is written to the trigger
          register, which will halt a sequence of chained transfers (default:
          ``True``).

        - *bswap*: ``bool`` If set to true, bytes in words or half-words will be reversed before
          writing (default: ``True``).

        - *sniff_en*: ``bool`` Set to ``True`` to allow data to be accessed by the chips sniff
          hardware (default: ``False``).

        - *write_err*: ``bool`` Setting this to ``True`` will clear a previously reported write
          error.

        - *read_err*: ``bool`` Setting this to ``True`` will clear a previously reported read
          error.

        See the description of the ``CH0_CTRL_TRIG`` register in section 2.5.7 of the RP2040
        datasheet for details of all of these fields.
        """
        ...

    def close(self) -> None:
        """
        Release the claim on the underlying DMA channel and free the interrupt
        handler. The :class:`DMA` object can not be used after this operation.
        """
        ...

    def config(
        self,
        read: int | AnyReadableBuf | None = None,
        write: int | AnyWritableBuf | None = None,
        count: int = -1,
        ctrl: int = -1,
        trigger: bool = False,
    ) -> None:
        """
        Configure the DMA registers for the channel and optionally start the transfer.
        Parameters are:

        - *read*: The address from which the DMA controller will start reading data or
          an object that will provide data to be read. It can be an integer or any
          object that supports the buffer protocol.
        - *write*: The address to which the DMA controller will start writing or an
          object into which data will be written. It can be an integer or any object
          that supports the buffer protocol.
        - *count*: The number of bus transfers that will execute before this channel
          stops. Note that this is the number of transfers, not the number of bytes.
          If the transfers are 2 or 4 bytes wide then the total amount of data moved
          (and thus the size of required buffer) needs to be multiplied accordingly.
        - *ctrl*: The value for the DMA control register. This is an integer value
          that is typically packed using the :meth:`DMA.pack_ctrl()`.
        - *trigger*: Optionally commence the transfer immediately.
        """
        ...

    def active(self, value: Any | None = None) -> bool:
        """
        Gets or sets whether the DMA channel is currently running.

        >>> sm.active()
        0
        >>> sm.active(1)
        >>> while sm.active():
        """
        ...

    def __init__(
        self,
        read: int | AnyReadableBuf | None = None,
        write: int | AnyWritableBuf | None = None,
        count: int = -1,
        ctrl: int = -1,
        trigger: bool = False,
    ) -> None: ...

class PIO:
    """
    Gets the PIO instance numbered *id*. The RP2040 has two PIO instances,
    numbered 0 and 1.

    Raises a ``ValueError`` if any other argument is provided.
    """

    JOIN_TX: Final[int] = 1
    JOIN_NONE: Final[int] = 0
    JOIN_RX: Final[int] = 2
    SHIFT_LEFT: Final[int] = 0
    OUT_HIGH: Final[int] = 3
    OUT_LOW: Final[int] = 2
    SHIFT_RIGHT: Final[int] = 1
    IN_LOW: Final[int] = 0
    IRQ_SM3: Final[int] = 2048
    IN_HIGH: Final[int] = 1
    IRQ_SM2: Final[int] = 1024
    IRQ_SM0: Final[int] = 256
    IRQ_SM1: Final[int] = 512
    def state_machine(self, id: int, program: _PIO_ASM_Program, *args, **kwargs) -> StateMachine:
        """
        Gets the state machine numbered *id*. On the RP2040, each PIO instance has
        four state machines, numbered 0 to 3.

        Optionally initialize it with a *program*: see `StateMachine.init`.

        >>> rp2.PIO(1).state_machine(3)
        StateMachine(7)
        """
        ...

    def remove_program(self, program: Optional[_PIO_ASM_Program] = None) -> None:
        """
        Remove *program* from the instruction memory of this PIO instance.

        If no program is provided, it removes all programs.

        It is not an error to remove a program which has already been removed.
        """
        ...

    def irq(
        self,
        handler: Optional[Callable[[PIO], None]] = None,
        trigger: _IRQ_TRIGGERS | None = None,
        hard: bool = False,
    ) -> _IRQ:
        """
        Returns the IRQ object for this PIO instance.

        MicroPython only uses IRQ 0 on each PIO instance. IRQ 1 is not available.

        Optionally configure it.
        """
        ...

    def add_program(self, program: _PIO_ASM_Program) -> None:
        """
        Add the *program* to the instruction memory of this PIO instance.

        The amount of memory available for programs on each PIO instance is
        limited. If there isn't enough space left in the PIO's program memory
        this method will raise ``OSError(ENOMEM)``.
        """
        ...

    def __init__(self, id) -> None: ...

class StateMachine:
    """
    Get the state machine numbered *id*. The RP2040 has two identical PIO
    instances, each with 4 state machines: so there are 8 state machines in
    total, numbered 0 to 7.

    Optionally initialize it with the given program *program*: see
    `StateMachine.init`.
    """

    def irq(self, handler=None, trigger=0 | 1, hard=False) -> _IRQ:
        """
        Returns the IRQ object for the given StateMachine.

        Optionally configure it.
        """
        ...

    def put(self, value, shift=0):
        """
        Push words onto the state machine's TX FIFO.

        *value* can be an integer, an array of type ``B``, ``H`` or ``I``, or a
        `bytearray`.

        This method will block until all words have been written to the FIFO.  If
        the FIFO is, or becomes, full, the method will block until the state machine
        pulls enough words to complete the write.

        Each word is first shifted left by *shift* bits, i.e. the state machine
        receives ``word << shift``.
        """
        ...

    def restart(self) -> None:
        """
        Restarts the state machine and jumps to the beginning of the program.

        This method clears the state machine's internal state using the RP2040's
        ``SM_RESTART`` register. This includes:

         - input and output shift counters
         - the contents of the input shift register
         - the delay counter
         - the waiting-on-IRQ state
         - a stalled instruction run using `StateMachine.exec()`
        """
        ...

    def rx_fifo(self) -> int:
        """
        Returns the number of words in the state machine's RX FIFO. A value of 0
        indicates the FIFO is empty.

        Useful for checking if data is waiting to be read, before calling
        `StateMachine.get()`.
        """
        ...

    def tx_fifo(self) -> int:
        """
        Returns the number of words in the state machine's TX FIFO. A value of 0
        indicates the FIFO is empty.

        Useful for checking if there is space to push another word using
        `StateMachine.put()`.
        """
        ...

    def init(
        self,
        program: _PIO_ASM_Program,
        *,
        freq: int = 1,
        in_base: Pin | None = None,
        out_base: Pin | None = None,
        set_base: Pin | None = None,
        jmp_pin: Pin | None = None,
        sideset_base: Pin | None = None,
        in_shiftdir: int | None = None,
        out_shiftdir: int | None = None,
        push_thresh: int | None = None,
        pull_thresh: int | None = None,
    ) -> None:
        """
        Configure the state machine instance to run the given *program*.

        The program is added to the instruction memory of this PIO instance. If the
        instruction memory already contains this program, then its offset is
        reused so as to save on instruction memory.

        - *freq* is the frequency in Hz to run the state machine at. Defaults to
          the system clock frequency.

          The clock divider is computed as ``system clock frequency / freq``, so
          there can be slight rounding errors.

          The minimum possible clock divider is one 65536th of the system clock: so
          at the default system clock frequency of 125MHz, the minimum value of
          *freq* is ``1908``. To run state machines at slower frequencies, you'll
          need to reduce the system clock speed with `machine.freq()`.
        - *in_base* is the first pin to use for ``in()`` instructions.
        - *out_base* is the first pin to use for ``out()`` instructions.
        - *set_base* is the first pin to use for ``set()`` instructions.
        - *jmp_pin* is the first pin to use for ``jmp(pin, ...)`` instructions.
        - *sideset_base* is the first pin to use for side-setting.
        - *in_shiftdir* is the direction the ISR will shift, either
          `PIO.SHIFT_LEFT` or `PIO.SHIFT_RIGHT`.
        - *out_shiftdir* is the direction the OSR will shift, either
          `PIO.SHIFT_LEFT` or `PIO.SHIFT_RIGHT`.
        - *push_thresh* is the threshold in bits before auto-push or conditional
          re-pushing is triggered.
        - *pull_thresh* is the threshold in bits before auto-pull or conditional
          re-pulling is triggered.
        """
        ...

    def exec(self, instr) -> None:
        """
        Execute a single PIO instruction.

        If *instr* is a string then uses `asm_pio_encode` to encode the instruction
        from the given string.

        >>> sm.exec("set(0, 1)")

        If *instr* is an integer then it is treated as an already encoded PIO
        machine code instruction to be executed.

        >>> sm.exec(rp2.asm_pio_encode("out(y, 8)", 0))
        """
        ...

    def get(self, buf=None, shift=0) -> Incomplete:
        """
        Pull a word from the state machine's RX FIFO.

        If the FIFO is empty, it blocks until data arrives (i.e. the state machine
        pushes a word).

        The value is shifted right by *shift* bits before returning, i.e. the
        return value is ``word >> shift``.
        """
        ...

    def active(self, value: Optional[Any] = None) -> bool:
        """
        Gets or sets whether the state machine is currently running.

        >>> sm.active()
        True
        >>> sm.active(0)
        False
        """
        ...

    def __init__(
        self,
        id: int,
        program: _PIO_ASM_Program,
        *,
        freq: int = 1,
        in_base: Pin | None = None,
        out_base: Pin | None = None,
        set_base: Pin | None = None,
        jmp_pin: Pin | None = None,
        sideset_base: Pin | None = None,
        in_shiftdir: int | None = None,
        out_shiftdir: int | None = None,
        push_thresh: int | None = None,
        pull_thresh: int | None = None,
    ) -> None: ...

class PIOASMEmit:
    """
    The PIOASMEmit class provides a comprehensive interface for constructing PIO programs,
    handling the intricacies of instruction encoding, label management, and program state.
    This allows users to build complex PIO programs in pythone, leveraging the flexibility
    and power of the PIO state machine.

    The class should not be instantiated directly, but used via the `@asm_pio` decorator.
    """

    def in_(self, src: int, data) -> _PIO_ASM_Program:
        """rp2.PIO IN instruction.

        Shift Bit count bits from Source into the Input Shift Register (ISR).
        Shift direction is configured for each state machine by SHIFTCTRL_IN_SHIFTDIR.
        Additionally, increase the input shift count by Bit count, saturating at 32.

        * Source:
            000: PINS
            001: X (scratch register X)
            010: Y (scratch register Y)
            011: NULL (all zeroes)
            100: Reserved
            101: Reserved
            110: ISR
            111: OSR
        * Bit count: How many bits to shift into the ISR. 1…32 bits, 32 is encoded as 00000.

        If automatic push is enabled, IN will also push the ISR contents to the RX FIFO if the push threshold is reached
        (SHIFTCTRL_PUSH_THRESH). IN still executes in one cycle, whether an automatic push takes place or not. The state machine
        will stall if the RX FIFO is full when an automatic push occurs. An automatic push clears the ISR contents to all-zeroes,
        and clears the input shift count.
        IN always uses the least significant Bit count bits of the source data. For example, if PINCTRL_IN_BASE is set to 5, the
        instruction IN PINS, 3 will take the values of pins 5, 6 and 7, and shift these into the ISR. First the ISR is shifted to the left
        or right to make room for the new input data, then the input data is copied into the gap this leaves. The bit order of the
        input data is not dependent on the shift direction.
        NULL can be used for shifting the ISR’s contents. For example, UARTs receive the LSB first, so must shift to the right.
        After 8 IN PINS, 1 instructions, the input serial data will occupy bits 31…24 of the ISR. An IN NULL, 24 instruction will shift
        in 24 zero bits, aligning the input data at ISR bits 7…0. Alternatively, the processor or DMA could perform a byte read
        from FIFO address + 3, which would take bits 31…24 of the FIFO contents.
        """
        ...

    def side(self, value: int):
        """rp2.PIO side modifier.
        This is a modifier which can be applied to any instruction, and is used to control side-set pin values.
        value: the value (bits) to output on the side-set pins

        When an instruction has side 0 next to it, the corresponding output is set LOW,
        and when it has side 1 next to it, the corresponding output is set HIGH.
        There can be up to 5 side-set pins, in which case side N is interpreted as a binary number.

        `side(0b00011)` sets the first and the second side-set pin HIGH, and the others LOW.
        """
        ...

    def out(self, destination: int, bit_count: int) -> _PIO_ASM_Program:
        """rp2.PIO OUT instruction.

        Shift Bit count bits out of the Output Shift Register (OSR), and write those bits to Destination.
        Additionally, increase the output shift count by Bit count, saturating at 32.

        Destination: (use lowercase in MicroPython)
            - 000: PINS
            - 001: X (scratch register X)
            - 010: Y (scratch register Y)
            - 011: NULL (discard data)
            - 100: PINDIRS
            - 101: PC
            - 110: ISR (also sets ISR shift counter to Bit count)
            - 111: EXEC (Execute OSR shift data as instruction)

        Bit_count:
            how many bits to shift out of the OSR. 1…32 bits, 32 is encoded as 00000.

        A 32-bit value is written to Destination: the lower Bit count bits come from the OSR, and the remainder are zeroes. This
        value is the least significant Bit count bits of the OSR if SHIFTCTRL_OUT_SHIFTDIR is to the right, otherwise it is the most
        significant bits.

        PINS and PINDIRS use the OUT pin mapping.

        If automatic pull is enabled, the OSR is automatically refilled from the TX FIFO if the pull threshold, SHIFTCTRL_PULL_THRESH,
        is reached. The output shift count is simultaneously cleared to 0. In this case, the OUT will stall if the TX FIFO is empty,
        but otherwise still executes in one cycle.

        OUT EXEC allows instructions to be included inline in the FIFO datastream. The OUT itself executes on one cycle, and the
        instruction from the OSR is executed on the next cycle. There are no restrictions on the types of instructions which can
        be executed by this mechanism. Delay cycles on the initial OUT are ignored, but the executee may insert delay cycles as
        normal.

        OUT PC behaves as an unconditional jump to an address shifted out from the OSR.
        """
        ...

    def jmp(self, condition, label: Incomplete | None = ...) -> _PIO_ASM_Program:
        """rp2.PIO JMP instruction.

        Set program counter to Address if Condition is true, otherwise no operation.
        Delay cycles on a JMP always take effect, whether Condition is true or false, and they take place after Condition is
        evaluated and the program counter is updated.

        Parameters:

        `condition`:
        - `None` : (no condition): Always
        - `not_x` : !X: scratch X zero
        - `x_dec` : X--: scratch X non-zero, prior to decrement
        - `not_y` : !Y: scratch Y zero
        - `y_dec` : Y--: scratch Y non-zero, prior to decrement
        - `x_not_y` : X!=Y: scratch X not equal scratch Y
        - `pin` : PIN: branch on input pin
        - `not_osre` : !OSRE: output shift register not empty

        `label`: Instruction address to jump to. In the instruction encoding, this is an absolute address within the PIO
        instruction memory.

        `JMP PIN` branches on the GPIO selected by EXECCTRL_JMP_PIN, a configuration field which selects one out of the maximum
        of 32 GPIO inputs visible to a state machine, independently of the state machine’s other input mapping. The branch is
        taken if the GPIO is high.

        `!OSRE` compares the bits shifted out since the last PULL with the shift count threshold configured by SHIFTCTRL_PULL_THRESH.
        This is the same threshold used by autopull.

        `JMP X--` and `JMP Y--` always decrement scratch register X or Y, respectively. The decrement is not conditional on the
        current value of the scratch register. The branch is conditioned on the initial value of the register, i.e. before the
        decrement took place: if the register is initially nonzero, the branch is taken.
        """
        ...

    def start_pass(self, pass_) -> None:
        """The start_pass method is used to start a pass over the instructions,
        setting up the necessary state for the pass. It handles wrapping instructions
        if needed and adjusts the delay maximum based on the number of side-set bits.
        """
        ...

    def wrap(self) -> None:
        """rp2.PIO WRAP directive.

        Placed after an instruction, this directive specifies the instruction after which,
        in normal control flow (i.e. jmp with false condition, or no jmp), the program
        wraps (to .wrap_target instruction). This directive is invalid outside of a
        program, may only be used once within a program, and if not specified
        defaults to after the last program instruction.
        """
        ...

    def word(self, instr, label: Incomplete | None = ...) -> _PIO_ASM_Program:
        """rp2.PIO instruction.

        Stores a raw 16-bit value as an instruction in the program. This directive is
        invalid outside of a program.
        """
        ...

    def wait(self, polarity: int, src: int, index: int, /) -> _PIO_ASM_Program:
        """rp2.PIO WAIT instruction.

        Stall until some condition is met.
        Like all stalling instructions, delay cycles begin after the instruction completes. That is, if any delay cycles are present,
        they do not begin counting until after the wait condition is met.

        Parameters:

            Polarity:
                1: wait for a 1.
                0: wait for a 0.

            Source: what to wait on. Values are:
                00: GPIO: System GPIO input selected by Index. This is an absolute GPIO index, and is not affected by the state machine’s input IO mapping.
                01: PIN: Input pin selected by Index. This state machine’s input IO mapping is applied first, and then Index
            selects which of the mapped bits to wait on. In other words, the pin is selected by adding Index to the
            PINCTRL_IN_BASE configuration, modulo 32.
                10: IRQ: PIO IRQ flag selected by Index
                11: Reserved

            Index: which pin or bit to check.

        WAIT x IRQ behaves slightly differently from other WAIT sources:
        * If Polarity is 1, the selected IRQ flag is cleared by the state machine upon the wait condition being met.
        * The flag index is decoded in the same way as the IRQ index field: if the MSB is set, the state machine ID (0…3) is
        added to the IRQ index, by way of modulo-4 addition on the two LSBs. For example, state machine 2 with a flag
        value of '0x11' will wait on flag 3, and a flag value of '0x13' will wait on flag 1. This allows multiple state machines
        running the same program to synchronise with each other.
        CAUTION
        WAIT 1 IRQ x should not be used with IRQ flags presented to the interrupt controller, to avoid a race condition with a
        system interrupt handler
        """
        ...

    def wrap_target(self) -> None:
        """rp2.PIO WRAP_TARGET directive.

        This directive specifies the instruction where
        execution continues due to program wrapping. This directive is invalid outside
        of a program, may only be used once within a program, and if not specified
        defaults to the start of the program
        """

    def delay(self, delay: int):
        """rp2.PIO delay modifier.

        The delay method allows setting a delay for the current instruction,
        ensuring it does not exceed the maximum allowed delay.
        """

    def label(self, label: str) -> None:
        """rp2.PIO instruction.

        Labels are of the form:

        <symbol>:

        or

        PUBLIC <symbol>:

        at the start of a line
        """
        ...

    def irq(self, mod, index: Incomplete | None = ...) -> _PIO_ASM_Program:
        """rp2.PIO instruction.

        Set or clear the IRQ flag selected by Index argument.
        * Clear: if 1, clear the flag selected by Index, instead of raising it. If Clear is set, the Wait bit has no effect.
        * Wait: if 1, halt until the raised flag is lowered again, e.g. if a system interrupt handler has acknowledged the flag.
        * Index:

            The 3 LSBs specify an IRQ index from 0-7. This IRQ flag will be set/cleared depending on the Clear bit.

            If the MSB is set, the state machine ID (0…3) is added to the IRQ index, by way of modulo-4 addition on the
            two LSBs. For example, state machine 2 with a flag value of 0x11 will raise flag 3, and a flag value of 0x13 will raise flag 1.

        IRQ flags 4-7 are visible only to the state machines; IRQ flags 0-3 can be routed out to system level interrupts, on either
        of the PIO’s two external interrupt request lines, configured by IRQ0_INTE and IRQ1_INTE.
        The modulo addition bit allows relative addressing of 'IRQ' and 'WAIT' instructions, for synchronising state machines
        which are running the same program. Bit 2 (the third LSB) is unaffected by this addition.
        If Wait is set, Delay cycles do not begin until after the wait period elapses."""

    def set(self, destination: int, data) -> _PIO_ASM_Program:
        """rp2.PIO SET instruction.

        Write immediate value Data to Destination.

        • Destination:
            000: PINS
            001: X (scratch register X) 5 LSBs are set to Data, all others cleared to 0.
            010: Y (scratch register Y) 5 LSBs are set to Data, all others cleared to 0.
            011: Reserved
            100: PINDIRS
            101: Reserved
            110: Reserved
            111: Reserved
        • Data: 5-bit immediate value to drive to pins or register.

        This can be used to assert control signals such as a clock or chip select, or to initialise loop counters. As Data is 5 bits in
        size, scratch registers can be SET to values from 0-31, which is sufficient for a 32-iteration loop.
        The mapping of SET and OUT onto pins is configured independently. They may be mapped to distinct locations, for
        example if one pin is to be used as a clock signal, and another for data. They may also be overlapping ranges of pins: a
        UART transmitter might use SET to assert start and stop bits, and OUT instructions to shift out FIFO data to the same pins.
        """
        ...

    def mov(self, dest, src, operation: int | None = None) -> _PIO_ASM_Program:
        """rp2.PIO MOV instruction.

        Copy data from Source to Destination.

        Destination:
            - 000: PINS (Uses same pin mapping as OUT)
            - 001: X (Scratch register X)
            - 010: Y (Scratch register Y)
            - 011: Reserved
            - 100: EXEC (Execute data as instruction)
            - 101: PC
            - 110: ISR (Input shift counter is reset to 0 by this operation, i.e. empty)
            - 111: OSR (Output shift counter is reset to 0 by this operation, i.e. full)

        Operation:
            - 00: None
            - 01: Invert (bitwise complement)
            - 10: Bit-reverse
            - 11: Reserved

        Source:
            - 000: PINS (Uses same pin mapping as IN)
            - 001: X
            - 010: Y
            - 011: NULL
            - 100: Reserved
            - 101: STATUS
            - 110: ISR
            - 111: OSR

        MOV PC causes an unconditional jump. MOV EXEC has the same behaviour as OUT EXEC (Section 3.4.5), and allows register
        contents to be executed as an instruction. The MOV itself executes in 1 cycle, and the instruction in Source on the next
        cycle. Delay cycles on MOV EXEC are ignored, but the executee may insert delay cycles as normal.
        The STATUS source has a value of all-ones or all-zeroes, depending on some state machine status such as FIFO
        full/empty, configured by EXECCTRL_STATUS_SEL.

        MOV can manipulate the transferred data in limited ways, specified by the Operation argument. Invert sets each bit in
        Destination to the logical NOT of the corresponding bit in Source, i.e. 1 bits become 0 bits, and vice versa. Bit reverse sets
        each bit n in Destination to bit 31 - n in Source, assuming the bits are numbered 0 to 31.
        MOV dst, PINS reads pins using the IN pin mapping, and writes the full 32-bit value to the destination without masking.
        The LSB of the read value is the pin indicated by PINCTRL_IN_BASE, and each successive bit comes from a higher numbered pin, wrapping after 31.

        """
        ...

    def push(self, value: int = ..., value2: int = ...) -> _PIO_ASM_Program:
        """rp2.PIO PUSH instruction.

        Push the contents of the ISR into the RX FIFO, as a single 32-bit word. Clear ISR to all-zeroes.
        * IfFull: If 1, do nothing unless the total input shift count has reached its threshold, SHIFTCTRL_PUSH_THRESH (the same
        as for autopush).
        * Block: If 1, stall execution if RX FIFO is full.

        PUSH IFFULL helps to make programs more compact, like autopush. It is useful in cases where the IN would stall at an
        inappropriate time if autopush were enabled, e.g. if the state machine is asserting some external control signal at this
        point.
        The PIO assembler sets the Block bit by default. If the Block bit is not set, the PUSH does not stall on a full RX FIFO, instead
        continuing immediately to the next instruction. The FIFO state and contents are unchanged when this happens. The ISR
        is still cleared to all-zeroes, and the FDEBUG_RXSTALL flag is set (the same as a blocking PUSH or autopush to a full RX FIFO)
        to indicate data was lost.

        """
        ...

    def pull(self, block: int = block, timeout: int = 0) -> _PIO_ASM_Program:
        """rp2.PIO PULL instruction.

        Load a 32-bit word from the TX FIFO into the OSR.
        * IfEmpty: If 1, do nothing unless the total output shift count has reached its threshold, SHIFTCTRL_PULL_THRESH (the
        same as for autopull).
        * Block: If 1, stall if TX FIFO is empty. If 0, pulling from an empty FIFO copies scratch X to OSR.

        Some peripherals (UART, SPI…) should halt when no data is available, and pick it up as it comes in; others (I2S) should
        clock continuously, and it is better to output placeholder or repeated data than to stop clocking. This can be achieved
        with the Block parameter.
        A nonblocking PULL on an empty FIFO has the same effect as MOV OSR, X. The program can either preload scratch register
        X with a suitable default, or execute a MOV X, OSR after each PULL NOBLOCK, so that the last valid FIFO word will be recycled
        until new data is available.

        PULL IFEMPTY is useful if an OUT with autopull would stall in an inappropriate location when the TX FIFO is empty. For
        example, a UART transmitter should not stall immediately after asserting the start bit. IfEmpty permits some of the same
        program simplifications as autopull, but the stall occurs at a controlled point in the program.

        NOTE:
        When autopull is enabled, any PULL instruction is a no-op when the OSR is full, so that the PULL instruction behaves as
        a barrier. OUT NULL, 32 can be used to explicitly discard the OSR contents. See the RP2040 Datasheet for more detail
        on autopull
        """
        ...

    def nop(self) -> _PIO_ASM_Program:
        """rp2.PIO NOP instruction.

        Assembles to mov y, y. "No operation", has no particular side effect, but a useful vehicle for a side-set
        operation or an extra delay.
        """
        ...

    def __init__(
        self,
        *,
        out_init: int | List | None = ...,
        set_init: int | List | None = ...,
        sideset_init: int | List | None = ...,
        in_shiftdir: int = ...,
        out_shiftdir: int = ...,
        autopush: bool = ...,
        autopull: bool = ...,
        push_thresh: int = ...,
        pull_thresh: int = ...,
        fifo_join: int = ...,
    ) -> None: ...
    @overload
    def __getitem__(self, key): ...
    @overload
    def __getitem__(self, key: int): ...
    @overload
    def __getitem__(self, key): ...
    @overload
    def __getitem__(self, key: int): ...

class Flash(AbstractBlockDev):
    """
    Gets the singleton object for accessing the SPI flash memory.
    """

    @overload
    def readblocks(self, block_num: int, buf: bytearray) -> bool:
        """
        The first form reads aligned, multiples of blocks.
        Starting at the block given by the index *block_num*, read blocks from
        the device into *buf* (an array of bytes).
        The number of blocks to read is given by the length of *buf*,
        which will be a multiple of the block size.
        """

    @overload
    def readblocks(self, block_num: int, buf: bytearray, offset: int) -> bool:
        """
        The second form allows reading at arbitrary locations within a block,
        and arbitrary lengths.
        Starting at block index *block_num*, and byte offset within that block
        of *offset*, read bytes from the device into *buf* (an array of bytes).
        The number of bytes to read is given by the length of *buf*.
        """

    @overload
    def writeblocks(self, block_num: int, buf: bytes | bytearray, /) -> None:
        """
        The first form writes aligned, multiples of blocks, and requires that the
        blocks that are written to be first erased (if necessary) by this method.
        Starting at the block given by the index *block_num*, write blocks from
        *buf* (an array of bytes) to the device.
        The number of blocks to write is given by the length of *buf*,
        which will be a multiple of the block size.
        """

    @overload
    def writeblocks(self, block_num: int, buf: bytes | bytearray, offset: int, /) -> None:
        """
        The second form allows writing at arbitrary locations within a block,
        and arbitrary lengths.  Only the bytes being written should be changed,
        and the caller of this method must ensure that the relevant blocks are
        erased via a prior ``ioctl`` call.
        Starting at block index *block_num*, and byte offset within that block
        of *offset*, write bytes from *buf* (an array of bytes) to the device.
        The number of bytes to write is given by the length of *buf*.

        Note that implementations must never implicitly erase blocks if the offset
        argument is specified, even if it is zero.
        """

    @overload
    def ioctl(self, op: int, arg) -> int | None: ...
    #
    @overload
    def ioctl(self, op: int) -> int | None:
        """
        These methods implement the simple and extended
        :ref:`block protocol <block-device-interface>` defined by
        :class:`vfs.AbstractBlockDev`.
        """

    def __init__(self) -> None: ...

class PIOASMError(Exception): ...
