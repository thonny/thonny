"""
asynchronous I/O scheduler for writing concurrent code.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/uasyncio.rst.

|see_cpython_module|
`asyncio <https://docs.python.org/3.8/library/asyncio.html>`_

Example::

    import uasyncio

    async def blink(led, period_ms):
        while True:
            led.on()
            await uasyncio.sleep_ms(5)
            led.off()
            await uasyncio.sleep_ms(period_ms)

    async def main(led1, led2):
        uasyncio.create_task(blink(led1, 700))
        uasyncio.create_task(blink(led2, 400))
        await uasyncio.sleep_ms(10_000)

    # Running on a pyboard
    from pyb import LED
    uasyncio.run(main(LED(1), LED(2)))

    # Running on a generic board
    from machine import Pin
    uasyncio.run(main(Pin(1), Pin(2)))
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from abc import ABC
from typing import Awaitable, TypeVar, Callable
from typing import Coroutine, Any, Dict, Iterable, Generic, Final

from uio import AnyReadableBuf

_T: Final = TypeVar("_T")
# `Coroutine` `_T` is covariant and `Awaitable` `_T` is invariant.
_C: Final = Coroutine[Any, None, _T] | Awaitable[_T]

class CancelledError(BaseException):
    """
   The operation has been cancelled.

   This exception can be caught to perform custom operations when asyncio Tasks are cancelled. 
   In almost all situations the exception must be re-raised.
   """

class IOQueue:
    """
   Queue and poller for stream IO.
   """

class SingletonGenerator:
    """
   `Yield` once, then raise StopIteration.
   """

class TimeoutError(Exception):
    """
   The operation has exceeded the given deadline.
   """

def run_until_complete(main_task: Awaitable[_T] | None = None, /):
    """
   Keep scheduling tasks until there are none left to schedule.
   """

def create_task(coro: _C, /) -> Task[_T]:
    """
    Create a new task from the given coroutine and schedule it to run.
    
    Returns the corresponding `Task` object.
   """

def current_task() -> Task[Any] | None:
    """
    Return the `Task` object associated with the currently running task.
   """

def run(coro: _C, /) -> _T:
    """
    Create a new task from the given coroutine and run it until it completes.
    
    Returns the value returned by *coro*.
   """

def sleep(t: float, /) -> Awaitable[None]:
    """
    Sleep for *t* seconds (can be a float).
    
    This is a coroutine.
   """

def sleep_ms(t: int, /) -> Awaitable[None]:
    """
    Sleep for *t* milliseconds.
    
    This is a coroutine, and a MicroPython extension.
   """

def wait_for(awaitable: Awaitable[_T], timeout: float, /) -> Awaitable[_T]:
    """
    Wait for the *awaitable* to complete, but cancel it if it takes longer
    than *timeout* seconds.  If *awaitable* is not a task then a task will be
    created from it.
    
    If a timeout occurs, it cancels the task and raises ``asyncio.TimeoutError``:
    this should be trapped by the caller.  The task receives
    ``asyncio.CancelledError`` which may be ignored or trapped using ``try...except``
    or ``try...finally`` to run cleanup code.
    
    Returns the return value of *awaitable*.
    
    This is a coroutine.
   """

def wait_for_ms(awaitable: Awaitable[_T], timeout: int, /) -> Awaitable[_T]:
    """
    Similar to `wait_for` but *timeout* is an integer in milliseconds.
    
    This is a coroutine, and a MicroPython extension.
   """

def gather(
    *awaitable: Awaitable[Any], return_exceptions: bool = False
) -> Awaitable[list[Any]]:
    """
    Run all *awaitables* concurrently.  Any *awaitables* that are not tasks are
    promoted to tasks.
    
    Returns a list of return values of all *awaitables*.
    
    This is a coroutine.
   """

StreamReader = "Stream"

StreamWriter = "Stream"

def open_connection(
    host: str | None, port: str | int | None, /,
) -> Awaitable[tuple[StreamReader, StreamWriter]]:
    """
    Open a TCP connection to the given *host* and *port*.  The *host* address will be
    resolved using `socket.getaddrinfo`, which is currently a blocking call.
    
    Returns a pair of streams: a reader and a writer stream.
    Will raise a socket-specific ``OSError`` if the host could not be resolved or if
    the connection could not be made.
    
    This is a coroutine.
   """

def start_server(
    callback: Callable[[StreamReader, StreamWriter], None],
    host: str | None,
    port: str | int | None,
    backlog: int = 5,
    /,
) -> Awaitable[Server]:
    """
    Start a TCP server on the given *host* and *port*.  The *callback* will be
    called with incoming, accepted connections, and be passed 2 arguments: reader
    and writer streams for the connection.
    
    Returns a `Server` object.
    
    This is a coroutine.
   """

def get_event_loop() -> Loop:
    """
    Return the event loop used to schedule and run tasks.  See `Loop`.
   """

def new_event_loop() -> Loop:
    """
    Reset the event loop and return it.
    
    Note: since MicroPython only has a single event loop this function just
    resets the loop's state, it does not create a new one.
   """

class Task(Awaitable[_T], Iterable[_T], Generic[_T], ABC):
    """
   class Task
   ----------
   """

    def __init__(self):
        """
       This object wraps a coroutine into a running task.  Tasks can be waited on
       using ``await task``, which will wait for the task to complete and return
       the return value of the task.
       
       Tasks should not be created directly, rather use `create_task` to create them.
      """
    def cancel(self) -> None:
        """
       Cancel the task by injecting ``asyncio.CancelledError`` into it.  The task may
       ignore this exception.  Cleanup code may be run by trapping it, or via
       ``try ... finally``.
      """

class Event:
    """
   class Event
   -----------
   """

    def __init__(self):
        """
       Create a new event which can be used to synchronise tasks.  Events start
       in the cleared state.
      """
    def is_set(self) -> bool:
        """
       Returns ``True`` if the event is set, ``False`` otherwise.
      """
    def set(self) -> None:
        """
       Set the event.  Any tasks waiting on the event will be scheduled to run.
       
       Note: This must be called from within a task. It is not safe to call this
       from an IRQ, scheduler callback, or other thread. See `ThreadSafeFlag`.
      """
    def clear(self) -> None:
        """
       Clear the event.
      """
    def wait(self) -> Awaitable[Any]:
        """
       Wait for the event to be set.  If the event is already set then it returns
       immediately.
       
       This is a coroutine.
      """

class ThreadSafeFlag:
    """
   class ThreadSafeFlag
   --------------------
   """

    def __init__(self):
        """
       Create a new flag which can be used to synchronise a task with code running
       outside the asyncio loop, such as other threads, IRQs, or scheduler
       callbacks.  Flags start in the cleared state.
      """
    def set(self) -> None:
        """
       Set the flag.  If there is a task waiting on the event, it will be scheduled
       to run.
      """
    def wait(self) -> Awaitable[None]:
        """
       Wait for the flag to be set.  If the flag is already set then it returns
       immediately.
       
       A flag may only be waited on by a single task at a time.
       
       This is a coroutine.
      """

class Lock(Awaitable[None], ABC):
    """
   class Lock
   ----------
   """

    def __init__(self):
        """
       Create a new lock which can be used to coordinate tasks.  Locks start in
       the unlocked state.
       
       In addition to the methods below, locks can be used in an ``async with`` statement.
      """
    def locked(self) -> bool:
        """
       Returns ``True`` if the lock is locked, otherwise ``False``.
      """
    def acquire(self) -> Awaitable[None]:
        """
       Wait for the lock to be in the unlocked state and then lock it in an atomic
       way.  Only one task can acquire the lock at any one time.
       
       This is a coroutine.
      """
    def release(self) -> None:
        """
       Release the lock.  If any tasks are waiting on the lock then the next one in the
       queue is scheduled to run and the lock remains locked.  Otherwise, no tasks are
       waiting an the lock becomes unlocked.
      """

class Stream:
    """

   """

    def __init__(self):
        """
       This represents a TCP stream connection.  To minimise code this class implements
       both a reader and a writer, and both ``StreamReader`` and ``StreamWriter`` alias to
       this class.
      """
    def get_extra_info(self, v: str, /) -> str:
        """
       Get extra information about the stream, given by *v*.  The valid values for *v* are:
       ``peername``.
      """
    def close(self) -> None:
        """
       Close the stream.
      """
    def wait_close(self) -> Awaitable[None]:
        """
       Wait for the stream to close.
       
       This is a coroutine.
      """
    def read(self, n: int, /) -> Awaitable[bytes]:
        """
       Read up to *n* bytes and return them.
       
       This is a coroutine.
      """
    def readline(self) -> Awaitable[bytes]:
        """
       Read a line and return it.
       
       This is a coroutine.
      """
    def write(self, buf: AnyReadableBuf, /) -> None:
        """
       Accumulated *buf* to the output buffer.  The data is only flushed when
       `Stream.drain` is called.  It is recommended to call `Stream.drain` immediately
       after calling this function.
      """
    def drain(self) -> Awaitable[None]:
        """
       Drain (write) all buffered output data out to the stream.
       
       This is a coroutine.
      """

class Server:
    """

   """

    def __init__(self):
        """
       This represents the server class returned from `start_server`.  It can be used
       in an ``async with`` statement to close the server upon exit.
      """
    def close(self) -> None:
        """
       Close the server.
      """
    def wait_close(self) -> Awaitable[None]:
        """
       Wait for the server to close.
       
       This is a coroutine.
      """

class Loop:
    """

   """

    def __init__(self):
        """
       This represents the object which schedules and runs tasks.  It cannot be
       created, use `get_event_loop` instead.
      """
    def create_task(self, coro: _C, /) -> Task[_T]:
        """
       Create a task from the given *coro* and return the new `Task` object.
      """
    def run_forever(self) -> None:
        """
       Run the event loop until `stop()` is called.
      """
    def run_until_complete(self, awaitable: Awaitable[_T], /) -> None:
        """
       Run the given *awaitable* until it completes.  If *awaitable* is not a task
       then it will be promoted to one.
      """
    def stop(self) -> None:
        """
       Stop the event loop.
      """
    def close(self) -> None:
        """
       Close the event loop.
      """
    def set_exception_handler(
        self, handler: Callable[[Loop, Dict[str, Any]], None] | None, /
    ) -> None:
        """
       Set the exception handler to call when a Task raises an exception that is not
       caught.  The *handler* should accept two arguments: ``(loop, context)``.
      """
    def get_exception_handler(self) -> Callable[[Loop, Dict[str, Any]], None] | None:
        """
       Get the current exception handler.  Returns the handler, or ``None`` if no
       custom handler is set.
      """
    def default_exception_handler(self, context: Dict[str, Any], /) -> None:
        """
       The default exception handler that is called.
      """
    def call_exception_handler(self, context: Dict[str, Any], /) -> None:
        """
       Call the current exception handler.  The argument *context* is passed through and
       is a dictionary containing keys: ``'message'``, ``'exception'``, ``'future'``.
      """
