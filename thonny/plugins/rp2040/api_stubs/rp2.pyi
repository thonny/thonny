from uarray import array
from machine import Pin
from typing import Sequence, Any, Iterable, Union

# make_stub_files: Wed 03 Feb 2021 at 08:12:32
class Flash:
    # Determined from: https://github.com/raspberrypi/micropython/blob/1196871a0f2f974b03915e08cfcc0433de4b8a64/ports/rp2/rp2_flash.c
    # Documentation put together via research and may be flawed!
    """
    Flash storage functionality.
    """

    CMD_INIT = 1
    CMD_DEINIT = 2
    CMD_SYNC = 3
    CMD_BLOCK_COUNT = 4
    CMD_BLOCK_SIZE = 5
    CMD_BLOCK_ERASE = 6

    def ioctl(self, cmd: int, offsetBlocks: int = None):
        """
        Send a command to the Flash storage controller.
        """

    def readblocks(self, offsetBlocks: int, buffer: bytearray):
        """
        Read data from the Flash storage.
        """

    def writeblocks(self, offsetBlocks: int, buffer: bytearray):
        """
        Write data to the Flash storage.
        """

class PIO:
    # Determined from: https://github.com/raspberrypi/micropython/blob/1196871a0f2f974b03915e08cfcc0433de4b8a64/ports/rp2/rp2_pio.c
    # Documentation put together via research and may be flawed!
    """
    Programmable I/O (PIO) functionality.

    The Pico has two PIO blocks that each have four state machines. 
    These are really stripped-down processing cores that can be used 
    to handle data coming in or out of the microcontroller, and 
    offload some of the processing requirement for implementing 
    communications protocols.
    """

    IN_HIGH = 1
    IN_LOW = 0
    IRQ_SM0 = 256
    IRQ_SM1 = 512
    IRQ_SM2 = 1024
    IRQ_SM3 = 2048
    OUT_HIGH = 3
    OUT_LOW = 2
    SHIFT_LEFT = 0
    SHIFT_RIGHT = 1
    JOIN_NONE = 0
    JOIN_TX = 1
    JOIN_RX = 2

    def __init__(self, pin:int) -> None: 
        ...

    def add_program(self, prog):
        """
        Adds program data to the PIO instruction memory.
        """

    def irq(self, handler=None, trigger=IRQ_SM0|IRQ_SM1|IRQ_SM2|IRQ_SM3, hard=False):
        """
        Execute assembly code when triggered.
        """

    def remove_program(self, prog = None):
        """
        Default to removing all programs from the PIO instruction
        memory, but will remove a specific program if passed as a 
        parameter.
        """

    def state_machine(self, id, prog, freq=-1, *, set=None) -> StateMachine:
        """
        Returns the StateMachine object.
        """

class PIOASMError(Exception): ...
class PIOASMEmit:
    def __init__(self) -> None: ...
    def start_pass(self, pass_: Any) -> None: ...
    def __getitem__(self, key: Any) -> Any: ...
        #   0: return self.delay(key)
        # ? 0: return self.delay(key)
    def delay(self, delay: int) -> PIOASMEmit: ...
        #   0: return self
        # ? 0: return self
    def side(self, value: Any) -> Any: ...
        #   0: return self
        # ? 0: return self
    def wrap_target(self) -> None: ...
    def wrap(self) -> None: ...
    def label(self, label: Any) -> None: ...
    def word(self, instr: Any, label: Any=None) -> Any: ...
        #   0: return self
        # ? 0: return self
    def nop(self) -> Any: ...
        #   0: return self.word()
        # ? 0: return self.word()
    def jmp(self, cond: Any, label: Any=None) -> Any: ...
        #   0: return self.word(|cond<<,label)
        # ? 0: return self.word(|cond<<, label)
    def wait(self, polarity: Any, src: Any, index: Any) -> Any: ...
        #   0: return self.word(|polarity<<|src<<|index)
        # ? 0: return self.word(|polarity<<|src<<|index)
    def in_(self, src: Any, data: Any) -> Any: ...
        #   0: return self.word(|src<<|data&)
        # ? 0: return self.word(|src<<|data&)
    def out(self, dest: Any, data: Any) -> Any: ...
        #   0: return self.word(|dest<<|data&)
        # ? 0: return self.word(|dest<<|data&)
    def push(self, value: Any=0, value2: Any=0) -> Any: ...
        #   0: return self.word(|value&)
        # ? 0: return self.word(|value&)
    def pull(self, value: Any=0, value2: Any=0) -> Any: ...
        #   0: return self.word(|value&)
        # ? 0: return self.word(|value&)
    def mov(self, dest: Any, src: Any) -> Any: ...
        #   0: return self.word(|dest<<|src)
        # ? 0: return self.word(|dest<<|src)
    def irq(self, mod: Any, index: Any=None) -> Any: ...
        #   0: return self.word(|mod&|index)
        # ? 0: return self.word(|mod&|index)
    def set(self, dest: Any, data: Any) -> Any: ...
        #   0: return self.word(|dest<<|data)
        # ? 0: return self.word(|dest<<|data)

class StateMachine:
    # Determined from: https://github.com/raspberrypi/micropython/blob/1196871a0f2f974b03915e08cfcc0433de4b8a64/ports/rp2/rp2_pio.c
    # Documentation put together via research and may be flawed!
    def __init__(self, id, prog, freq: int=-1, *, in_base: Pin=None, out_base: Pin=None, set_base: Pin=None, jmp_pin: Pin=None, sideset_base: Pin=None, in_shiftdir: int=None, out_shiftdir: int=None, push_thresh: int=None, pull_thresh: int=None):
        """
        Create a new StateMachine containing two First-In-First-Out (FIFO)
        structures: one for incoming data and another for outgoing data.

        The input FIFO is known as the RX FIFO and the output FIFO is known
        as the TX FIFO.

        Each FIFO can contain up to four words of data (each 32 bits) and can
        be linked to Direct Memory Access (DMA).

        The FIFO structures are linked to the state machine via the input and
        output shift registers called X and Y. These are for storing temporary
        data.

        A Pico board has 8 available state machines.

            - *id* should be a number between 0 and 7 (the Pico has 8 machines).
            - *prog* is the assembly code to execute (decorated by ``@asm_pio``).
            - *freq* is the frequency at which the code should be executed (in milliseconds).
        """

    def init(self, id, prog, freq: int=-1, *, in_base: Pin=None, out_base: Pin=None, set_base: Pin=None, jmp_pin: Pin=None, sideset_base: Pin=None, in_shiftdir: int=None, out_shiftdir: int=None, push_thresh: int=None, pull_thresh: int=None):
        """
        Create a new StateMachine containing two First-In-First-Out (FIFO)
        structures: one for incoming data and another for outgoing data.

        The input FIFO is known as the RX FIFO and the output FIFO is known
        as the TX FIFO.

        Each FIFO can contain up to four words of data (each 32 bits) and can
        be linked to Direct Memory Access (DMA).

        The FIFO structures are linked to the state machine via the input and
        output shift registers called X and Y. These are for storing temporary
        data.

        A Pico board has 8 available state machines.

            - *id* should be a number between 0 and 7 (the Pico has 8 machines).
            - *prog* is the assembly code to execute (decorated by ``@asm_pio``).
            - *freq* is the frequency at which the code should be executed (in milliseconds).
        """

    def exec(self, instr: str):
        """
        Run an execution instruction.
        """

    def irq(self, handler=None, trigger=0|1, hard=False):
        """
        Set an IRQ handler.
        """

    def active(self, value: int):
        """
        Set the ``StateMachine`` to be active.

            - *value* should be 1 for active.
        """

    def get(self, buf: bytes=None, shift: int=0):
        """
        Get data from the ``StateMachine``.

            - *buf* are optional bytes
            - *shift* is an optional number of places to shift.
        """
    
    def put(self, value: Union[bytes, int | array[int]], shift: int=0):
        """
        Sets data within the ``StateMachine``.

            - *buf* are optional bytes
            - *shift* is an optional number of places to shift.
        """
    def restart(self):
        """
        ``Restarts`` the state machine.

            - it resets the statemachine to the initial state without the need to re-instantiation.
            - It also makes PIO code easier, because then stalling as error state can be unlocked.
        """
    def rx_fifo(self) -> int:
        """
        Return the number of ``RX FIFO`` items. 0 if empty

            - rx_fifo() is also useful, for MP code to check for data & timeout if no data arrived. 
        """
    def tx_fifo(self) -> int:
        """
        Return the number of ``TX FIFO`` items. 0 if empty

            - tx_fifo() can be useful to check states where data is not processed.
        """

def asm_pio(
    out_init: int = None,
    set_init: int = None,
    sideset_init: int = None,
    in_shiftdir: int = 0,
    out_shiftdir: int = 0,
    autopush: bool = False,
    autopull: bool = False,
    push_thresh: int = 32,
    pull_thresh: int = 32,
    fifo_join=0,
) -> Any:
    """
    This decorator lets MicroPython know that the method is written in PIO assembly.

    You should disable linting since the content isn't written in Python.

    In Pylance, move any assembly code into a separate file and ensure the first
    line of that file reads: ``# type: ignore``.

    In Pylint, add a comment that reads ``# pylint: disable=E,W,C,R`` at the beginning of 
    the method.
    """
    #   0: return emit.prog
    # ? 0: return emit.prog
    #   1: return dec
    # ? 1: return dec

def asm_pio_encode(instr: str, sideset_count: int) -> Any: ...
    #   0: return emit.prog[_PROG_DATA][]
    # ? 0: return emit.prog[_PROG_DATA][]

def const(value:Any) -> Any:
    pass