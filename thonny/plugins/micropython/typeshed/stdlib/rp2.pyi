"""
Functionality specific to the RP2.

MicroPython module: https://docs.micropython.org/en/v1.23.0/library/rp2.html

The ``rp2`` module contains functions and classes specific to the RP2040, as
used in the Raspberry Pi Pico.

See the `RP2040 Python datasheet
<https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf>`_
for more information, and `pico-micropython-examples
<https://github.com/raspberrypi/pico-micropython-examples/tree/master/pio>`_
for example code.

---
Module: 'rp2' on micropython-v1.23.0-rp2-RPI_PICO
"""

# MCU: {'build': '', 'ver': '1.23.0', 'version': '1.23.0', 'port': 'rp2', 'board': 'RPI_PICO', 'mpy': 'v6.3', 'family': 'micropython', 'cpu': 'RP2040', 'arch': 'armv6m'}
# Stubber: v1.23.0
from __future__ import annotations
from _typeshed import Incomplete
from typing import Any, Optional

_pio_funcs: dict = {}

def asm_pio_encode(instr, sideset_count, sideset_opt=False) -> Incomplete:
    """
    Assemble a single PIO instruction. You usually want to use `asm_pio()`
    instead.

    >>> rp2.asm_pio_encode("set(0, 1)", 0)
    57345
    """
    ...

def asm_pio(
    *,
    out_init=None,
    set_init=None,
    sideset_init=None,
    in_shiftdir=0,
    out_shiftdir=0,
    autopush=False,
    autopull=False,
    push_thresh=32,
    pull_thresh=32,
    fifo_join=PIO.JOIN_NONE,
) -> Incomplete:
    """
    Assemble a PIO program.

    The following parameters control the initial state of the GPIO pins, as one
    of `PIO.IN_LOW`, `PIO.IN_HIGH`, `PIO.OUT_LOW` or `PIO.OUT_HIGH`. If the
    program uses more than one pin, provide a tuple, e.g.
    ``out_init=(PIO.OUT_LOW, PIO.OUT_LOW)``.

    - *out_init* configures the pins used for ``out()`` instructions.
    - *set_init* configures the pins used for ``set()`` instructions. There can
      be at most 5.
    - *sideset_init* configures the pins used side-setting. There can be at
      most 5.

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

def bootsel_button() -> Incomplete:
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

def const(*args, **kwargs) -> Incomplete: ...

class PIOASMEmit:
    def in_(self, *args, **kwargs) -> Incomplete: ...
    def side(self, *args, **kwargs) -> Incomplete: ...
    def out(self, *args, **kwargs) -> Incomplete: ...
    def jmp(self, *args, **kwargs) -> Incomplete: ...
    def start_pass(self, *args, **kwargs) -> Incomplete: ...
    def wrap(self, *args, **kwargs) -> Incomplete: ...
    def word(self, *args, **kwargs) -> Incomplete: ...
    def wait(self, *args, **kwargs) -> Incomplete: ...
    def wrap_target(self, *args, **kwargs) -> Incomplete: ...
    def delay(self, *args, **kwargs) -> Incomplete: ...
    def label(self, *args, **kwargs) -> Incomplete: ...
    def irq(self, *args, **kwargs) -> Incomplete: ...
    def set(self, *args, **kwargs) -> Incomplete: ...
    def mov(self, *args, **kwargs) -> Incomplete: ...
    def push(self, *args, **kwargs) -> Incomplete: ...
    def pull(self, *args, **kwargs) -> Incomplete: ...
    def nop(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...

class PIOASMError(Exception): ...

class PIO:
    """
    Gets the PIO instance numbered *id*. The RP2040 has two PIO instances,
    numbered 0 and 1.

    Raises a ``ValueError`` if any other argument is provided.
    """

    JOIN_TX: int = 1
    JOIN_NONE: int = 0
    JOIN_RX: int = 2
    SHIFT_LEFT: int = 0
    OUT_HIGH: int = 3
    OUT_LOW: int = 2
    SHIFT_RIGHT: int = 1
    IN_LOW: int = 0
    IRQ_SM3: int = 2048
    IN_HIGH: int = 1
    IRQ_SM2: int = 1024
    IRQ_SM0: int = 256
    IRQ_SM1: int = 512
    def state_machine(self, id, program, *args, **kwargs) -> Incomplete:
        """
        Gets the state machine numbered *id*. On the RP2040, each PIO instance has
        four state machines, numbered 0 to 3.

        Optionally initialize it with a *program*: see `StateMachine.init`.

        >>> rp2.PIO(1).state_machine(3)
        StateMachine(7)
        """
        ...

    def remove_program(self, program: Optional[Any] = None) -> None:
        """
        Remove *program* from the instruction memory of this PIO instance.

        If no program is provided, it removes all programs.

        It is not an error to remove a program which has already been removed.
        """
        ...

    def irq(self, handler=None, trigger=IRQ_SM0, hard=False) -> Incomplete:
        """
        Returns the IRQ object for this PIO instance.

        MicroPython only uses IRQ 0 on each PIO instance. IRQ 1 is not available.

        Optionally configure it.
        """
        ...

    def add_program(self, program) -> Incomplete:
        """
        Add the *program* to the instruction memory of this PIO instance.

        The amount of memory available for programs on each PIO instance is
        limited. If there isn't enough space left in the PIO's program memory
        this method will raise ``OSError(ENOMEM)``.
        """
        ...

    def __init__(self, *argv, **kwargs) -> None: ...

class StateMachine:
    """
    Get the state machine numbered *id*. The RP2040 has two identical PIO
    instances, each with 4 state machines: so there are 8 state machines in
    total, numbered 0 to 7.

    Optionally initialize it with the given program *program*: see
    `StateMachine.init`.
    """

    def irq(self, handler=None, trigger=0 | 1, hard=False) -> Incomplete:
        """
        Returns the IRQ object for the given StateMachine.

        Optionally configure it.
        """
        ...

    def put(self, value, shift=0) -> Incomplete:
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

    def restart(self) -> Incomplete:
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
        program,
        freq=-1,
        *,
        in_base=None,
        out_base=None,
        set_base=None,
        jmp_pin=None,
        sideset_base=None,
        in_shiftdir=None,
        out_shiftdir=None,
        push_thresh=None,
        pull_thresh=None,
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

    def exec(self, instr) -> Incomplete:
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

    def active(self, value: Optional[Any] = None) -> Incomplete:
        """
        Gets or sets whether the state machine is currently running.

        >>> sm.active()
        True
        >>> sm.active(0)
        False
        """
        ...

    def __init__(self, *argv, **kwargs) -> None: ...

class DMA:
    """
    Claim one of the DMA controller channels for exclusive use.
    """

    def irq(self, handler=None, hard=False) -> Incomplete:
        """
        Returns the IRQ object for this DMA channel and optionally configures it.
        """
        ...

    def unpack_ctrl(self, value) -> Incomplete:
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

    def pack_ctrl(self, default=None, **kwargs) -> Incomplete:
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

    def close(self) -> Incomplete:
        """
        Release the claim on the underlying DMA channel and free the interrupt
        handler. The :class:`DMA` object can not be used after this operation.
        """
        ...

    def config(self, read=None, write=None, count=None, ctrl=None, trigger=False) -> None:
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

    def active(self, value: Optional[Any] = None) -> Incomplete:
        """
        Gets or sets whether the DMA channel is currently running.

        >>> sm.active()
        0
        >>> sm.active(1)
        >>> while sm.active():
        """
        ...

    def __init__(self, *argv, **kwargs) -> None: ...

class Flash:
    """
    Gets the singleton object for accessing the SPI flash memory.
    """

    def readblocks(self, block_num, buf, offset: Optional[int] = 0) -> Incomplete: ...
    def writeblocks(self, block_num, buf, offset: Optional[int] = 0) -> Incomplete: ...
    def ioctl(self, cmd, arg) -> Incomplete:
        """
        These methods implement the simple and extended
        :ref:`block protocol <block-device-interface>` defined by
        :class:`vfs.AbstractBlockDev`.
        """
        ...

    def __init__(self, *argv, **kwargs) -> None: ...
