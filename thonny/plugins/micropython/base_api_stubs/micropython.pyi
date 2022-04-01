"""
access and control MicroPython internals.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/micropython.rst.
==============================================================

.. module:: micropython
   :synopsis: access and control MicroPython internals
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import TypeVar, overload, Callable, Any, Final

_T: Final = TypeVar("_T")
_F: Final = TypeVar("_F", bound=Callable[..., Any])

def native(func: _F) -> _F:
    """
   This causes the MicroPython compiler to emit unoptimised native CPU opcodes
   rather than bytecode (normal) or optimised opcodes (viper) and is an optimisation,
   for more information see 
   https://docs.micropython.org/en/latest/reference/speed_python.html#the-native-code-emitter.
   """

def viper(func: _F) -> _F:
    """
   This causes the MicroPython compiler to emit optimised native CPU opcodes based on special typehints
   rather than bytecode (normal) or unoptimised opcodes (native) and is an optimisation,
   for more information see 
   https://docs.micropython.org/en/latest/reference/speed_python.html#the-viper-code-emitter.
   """

def const(expr: _T, /) -> _T:
    """
   Used to declare that the expression is a constant so that the compile can
   optimise it.  The use of this function should be as follows::
   
    from micropython import const
   
    CONST_X = const(123)
    CONST_Y = const(2 * CONST_X + 1)
   
   Constants declared this way are still accessible as global variables from
   outside the module they are declared in.  On the other hand, if a constant
   begins with an underscore then it is hidden, it is not available as a global
   variable, and does not take up any memory during execution.
   
   This `const` function is recognised directly by the MicroPython parser and is
   provided as part of the :mod:`micropython` module mainly so that scripts can be
   written which run under both CPython and MicroPython, by following the above
   pattern.
   """

@overload
def opt_level() -> int:
    """
   If *level* is given then this function sets the optimisation level for subsequent
   compilation of scripts, and returns ``None``.  Otherwise it returns the current
   optimisation level.
   
   The optimisation level controls the following compilation features:
   
   - Assertions: at level 0 assertion statements are enabled and compiled into the
     bytecode; at levels 1 and higher assertions are not compiled.
   - Built-in ``__debug__`` variable: at level 0 this variable expands to ``True``;
     at levels 1 and higher it expands to ``False``.
   - Source-code line numbers: at levels 0, 1 and 2 source-code line number are
     stored along with the bytecode so that exceptions can report the line number
     they occurred at; at levels 3 and higher line numbers are not stored.
   
   The default optimisation level is usually level 0.
   """

@overload
def opt_level(level: int, /) -> None:
    """
   If *level* is given then this function sets the optimisation level for subsequent
   compilation of scripts, and returns ``None``.  Otherwise it returns the current
   optimisation level.
   
   The optimisation level controls the following compilation features:
   
   - Assertions: at level 0 assertion statements are enabled and compiled into the
     bytecode; at levels 1 and higher assertions are not compiled.
   - Built-in ``__debug__`` variable: at level 0 this variable expands to ``True``;
     at levels 1 and higher it expands to ``False``.
   - Source-code line numbers: at levels 0, 1 and 2 source-code line number are
     stored along with the bytecode so that exceptions can report the line number
     they occurred at; at levels 3 and higher line numbers are not stored.
   
   The default optimisation level is usually level 0.
   """

def alloc_emergency_exception_buf(size: int, /) -> None:
    """
   Allocate *size* bytes of RAM for the emergency exception buffer (a good
   size is around 100 bytes).  The buffer is used to create exceptions in cases
   when normal RAM allocation would fail (eg within an interrupt handler) and
   therefore give useful traceback information in these situations.
   
   A good way to use this function is to put it at the start of your main script
   (eg ``boot.py`` or ``main.py``) and then the emergency exception buffer will be active
   for all the code following it.
   """

@overload
def mem_info() -> None:
    """
   Print information about currently used memory.  If the *verbose* argument
   is given then extra information is printed.
   
   The information that is printed is implementation dependent, but currently
   includes the amount of stack and heap used.  In verbose mode it prints out
   the entire heap indicating which blocks are used and which are free.
   """

@overload
def mem_info(verbose: Any, /) -> None:
    """
   Print information about currently used memory.  If the *verbose* argument
   is given then extra information is printed.
   
   The information that is printed is implementation dependent, but currently
   includes the amount of stack and heap used.  In verbose mode it prints out
   the entire heap indicating which blocks are used and which are free.
   """

@overload
def qstr_info() -> None:
    """
   Print information about currently interned strings.  If the *verbose*
   argument is given then extra information is printed.
   
   The information that is printed is implementation dependent, but currently
   includes the number of interned strings and the amount of RAM they use.  In
   verbose mode it prints out the names of all RAM-interned strings.
   """

@overload
def qstr_info(verbose: bool, /) -> None:
    """
   Print information about currently interned strings.  If the *verbose*
   argument is given then extra information is printed.
   
   The information that is printed is implementation dependent, but currently
   includes the number of interned strings and the amount of RAM they use.  In
   verbose mode it prints out the names of all RAM-interned strings.
   """

def stack_use() -> int:
    """
   Return an integer representing the current amount of stack that is being
   used.  The absolute value of this is not particularly useful, rather it
   should be used to compute differences in stack usage at different points.
   """

def heap_lock() -> None:
    """
   Lock or unlock the heap.  When locked no memory allocation can occur and a
   `MemoryError` will be raised if any heap allocation is attempted.
   `heap_locked()` returns a true value if the heap is currently locked.
   
   These functions can be nested, ie `heap_lock()` can be called multiple times
   in a row and the lock-depth will increase, and then `heap_unlock()` must be
   called the same number of times to make the heap available again.
   
   Both `heap_unlock()` and `heap_locked()` return the current lock depth
   (after unlocking for the former) as a non-negative integer, with 0 meaning
   the heap is not locked.
   
   If the REPL becomes active with the heap locked then it will be forcefully
   unlocked.
   
   Note: `heap_locked()` is not enabled on most ports by default,
   requires ``MICROPY_PY_MICROPYTHON_HEAP_LOCKED``.
   """

def heap_unlock() -> None:
    """
   Lock or unlock the heap.  When locked no memory allocation can occur and a
   `MemoryError` will be raised if any heap allocation is attempted.
   `heap_locked()` returns a true value if the heap is currently locked.
   
   These functions can be nested, ie `heap_lock()` can be called multiple times
   in a row and the lock-depth will increase, and then `heap_unlock()` must be
   called the same number of times to make the heap available again.
   
   Both `heap_unlock()` and `heap_locked()` return the current lock depth
   (after unlocking for the former) as a non-negative integer, with 0 meaning
   the heap is not locked.
   
   If the REPL becomes active with the heap locked then it will be forcefully
   unlocked.
   
   Note: `heap_locked()` is not enabled on most ports by default,
   requires ``MICROPY_PY_MICROPYTHON_HEAP_LOCKED``.
   """

def heap_locked() -> bool:
    """
   Lock or unlock the heap.  When locked no memory allocation can occur and a
   `MemoryError` will be raised if any heap allocation is attempted.
   `heap_locked()` returns a true value if the heap is currently locked.
   
   These functions can be nested, ie `heap_lock()` can be called multiple times
   in a row and the lock-depth will increase, and then `heap_unlock()` must be
   called the same number of times to make the heap available again.
   
   Both `heap_unlock()` and `heap_locked()` return the current lock depth
   (after unlocking for the former) as a non-negative integer, with 0 meaning
   the heap is not locked.
   
   If the REPL becomes active with the heap locked then it will be forcefully
   unlocked.
   
   Note: `heap_locked()` is not enabled on most ports by default,
   requires ``MICROPY_PY_MICROPYTHON_HEAP_LOCKED``.
   """

def kbd_intr(chr: int) -> None:
    """
   Set the character that will raise a `KeyboardInterrupt` exception.  By
   default this is set to 3 during script execution, corresponding to Ctrl-C.
   Passing -1 to this function will disable capture of Ctrl-C, and passing 3
   will restore it.
   
   This function can be used to prevent the capturing of Ctrl-C on the
   incoming stream of characters that is usually used for the REPL, in case
   that stream is used for other purposes.
   """

def schedule(func: Callable[[_T], None], arg: _T, /) -> None:
    """
   Schedule the function *func* to be executed "very soon".  The function
   is passed the value *arg* as its single argument.  "Very soon" means that
   the MicroPython runtime will do its best to execute the function at the
   earliest possible time, given that it is also trying to be efficient, and
   that the following conditions hold:
   
   - A scheduled function will never preempt another scheduled function.
   - Scheduled functions are always executed "between opcodes" which means
     that all fundamental Python operations (such as appending to a list)
     are guaranteed to be atomic.
   - A given port may define "critical regions" within which scheduled
     functions will never be executed.  Functions may be scheduled within
     a critical region but they will not be executed until that region
     is exited.  An example of a critical region is a preempting interrupt
     handler (an IRQ).
   
   A use for this function is to schedule a callback from a preempting IRQ.
   Such an IRQ puts restrictions on the code that runs in the IRQ (for example
   the heap may be locked) and scheduling a function to call later will lift
   those restrictions.
   
   Note: If `schedule()` is called from a preempting IRQ, when memory
   allocation is not allowed and the callback to be passed to `schedule()` is
   a bound method, passing this directly will fail. This is because creating a
   reference to a bound method causes memory allocation. A solution is to
   create a reference to the method in the class constructor and to pass that
   reference to `schedule()`. This is discussed in detail here
   :ref:`reference documentation <isr_rules>` under "Creation of Python
   objects".
   
   There is a finite queue to hold the scheduled functions and `schedule()`
   will raise a `RuntimeError` if the queue is full.
   """
