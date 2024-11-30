import _thread
import sys
from _thread import _excepthook, _ExceptHookArgs, get_native_id as get_native_id
from _typeshed import ProfileFunction, TraceFunction
from collections.abc import Callable, Iterable, Mapping
from types import TracebackType
from typing import Any, TypeVar, final

_T = TypeVar("_T")

__all__ = [
    "get_ident",
    "active_count",
    "Condition",
    "current_thread",
    "enumerate",
    "main_thread",
    "TIMEOUT_MAX",
    "Event",
    "Lock",
    "RLock",
    "Semaphore",
    "BoundedSemaphore",
    "Thread",
    "Barrier",
    "BrokenBarrierError",
    "Timer",
    "ThreadError",
    "ExceptHookArgs",
    "setprofile",
    "settrace",
    "local",
    "stack_size",
    "excepthook",
    "get_native_id",
]

if sys.version_info >= (3, 10):
    __all__ += ["getprofile", "gettrace"]

if sys.version_info >= (3, 12):
    __all__ += ["setprofile_all_threads", "settrace_all_threads"]

_profile_hook: ProfileFunction | None

def active_count() -> int: ...
def activeCount() -> int: ...  # deprecated alias for active_count()
def current_thread() -> Thread: ...
def currentThread() -> Thread: ...  # deprecated alias for current_thread()
def get_ident() -> int:
    """
    Return a non-zero integer that uniquely identifies the current thread
    amongst other threads that exist simultaneously.
    This may be used to identify per-thread resources.
    Even though on some platforms threads identities may appear to be
    allocated consecutive numbers starting at 1, this behavior should not
    be relied upon, and the number should be seen purely as a magic cookie.
    A thread's identity may be reused for another thread after it exits.
    """
    ...
def enumerate() -> list[Thread]: ...
def main_thread() -> Thread: ...
def settrace(func: TraceFunction) -> None: ...
def setprofile(func: ProfileFunction | None) -> None: ...

if sys.version_info >= (3, 12):
    def setprofile_all_threads(func: ProfileFunction | None) -> None: ...
    def settrace_all_threads(func: TraceFunction) -> None: ...

if sys.version_info >= (3, 10):
    def gettrace() -> TraceFunction | None: ...
    def getprofile() -> ProfileFunction | None: ...

def stack_size(size: int = 0, /) -> int:
    """
    Return the thread stack size used when creating new threads.  The
    optional size argument specifies the stack size (in bytes) to be used
    for subsequently created threads, and must be 0 (use platform or
    configured default) or a positive integer value of at least 32,768 (32k).
    If changing the thread stack size is unsupported, a ThreadError
    exception is raised.  If the specified size is invalid, a ValueError
    exception is raised, and the stack size is unmodified.  32k bytes
     currently the minimum supported stack size value to guarantee
    sufficient stack space for the interpreter itself.

    Note that some platforms may have particular restrictions on values for
    the stack size, such as requiring a minimum stack size larger than 32 KiB or
    requiring allocation in multiples of the system memory page size
    - platform documentation should be referred to for more information
    (4 KiB pages are common; using multiples of 4096 for the stack size is
    the suggested approach in the absence of more specific information).
    """
    ...

TIMEOUT_MAX: float

ThreadError = _thread.error
local = _thread._local

class Thread:
    name: str
    @property
    def ident(self) -> int | None:
        """
        Thread identifier of this thread or None if it has not been started.

        This is a nonzero integer. See the get_ident() function. Thread
        identifiers may be recycled when a thread exits and another thread is
        created. The identifier is available even after the thread has exited.
        """
        ...
    daemon: bool
    def __init__(
        self,
        group: None = None,
        target: Callable[..., object] | None = None,
        name: str | None = None,
        args: Iterable[Any] = (),
        kwargs: Mapping[str, Any] | None = None,
        *,
        daemon: bool | None = None,
    ) -> None: ...
    def start(self) -> None: ...
    def run(self) -> None: ...
    def join(self, timeout: float | None = None) -> None: ...
    @property
    def native_id(self) -> int | None:
        """
        Native integral thread ID of this thread, or None if it has not been started.

        This is a non-negative integer. See the get_native_id() function.
        This represents the Thread ID as reported by the kernel.
        """
        ...
    def is_alive(self) -> bool: ...
    if sys.version_info < (3, 9):
        def isAlive(self) -> bool: ...
    # the following methods are all deprecated
    def getName(self) -> str: ...
    def setName(self, name: str) -> None: ...
    def isDaemon(self) -> bool: ...
    def setDaemon(self, daemonic: bool) -> None: ...

class _DummyThread(Thread):
    def __init__(self) -> None: ...

@final
class Lock:
    """
    A lock object is a synchronization primitive.  To create a lock,
    call threading.Lock().  Methods are:

    acquire() -- lock the lock, possibly blocking until it can be obtained
    release() -- unlock of the lock
    locked() -- test whether the lock is currently locked

    A lock is not owned by the thread that locked it; another thread may
    unlock it.  A thread attempting to lock a lock that it has already locked
    will block until another thread unlocks it.  Deadlocks may ensue.
    """
    def __enter__(self) -> bool:
        """Lock the lock."""
        ...
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Release the lock."""
        ...
    def acquire(self, blocking: bool = ..., timeout: float = ...) -> bool:
        """
        Lock the lock.  Without argument, this blocks if the lock is already
        locked (even by the same thread), waiting for another thread to release
        the lock, and return True once the lock is acquired.
        With an argument, this will only block if the argument is true,
        and the return value reflects whether the lock is acquired.
        The blocking operation is interruptible.
        """
        ...
    def release(self) -> None:
        """
        Release the lock, allowing another thread that is blocked waiting for
        the lock to acquire the lock.  The lock must be in the locked state,
        but it needn't be locked by the same thread that unlocks it.
        """
        ...
    def locked(self) -> bool:
        """Return whether the lock is in the locked state."""
        ...
    def acquire_lock(self, blocking: bool = ..., timeout: float = ...) -> bool:
        """An obsolete synonym of acquire()."""
        ...
    def release_lock(self) -> None:
        """An obsolete synonym of release()."""
        ...
    def locked_lock(self) -> bool:
        """An obsolete synonym of locked()."""
        ...

@final
class _RLock:
    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool: ...
    def release(self) -> None: ...
    __enter__ = acquire
    def __exit__(self, t: type[BaseException] | None, v: BaseException | None, tb: TracebackType | None) -> None: ...

RLock = _RLock

class Condition:
    def __init__(self, lock: Lock | _RLock | None = None) -> None: ...
    def __enter__(self) -> bool: ...
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None: ...
    def acquire(self, blocking: bool = ..., timeout: float = ...) -> bool: ...
    def release(self) -> None: ...
    def wait(self, timeout: float | None = None) -> bool: ...
    def wait_for(self, predicate: Callable[[], _T], timeout: float | None = None) -> _T: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...
    def notifyAll(self) -> None: ...  # deprecated alias for notify_all()

class Semaphore:
    _value: int
    def __init__(self, value: int = 1) -> None: ...
    def __exit__(self, t: type[BaseException] | None, v: BaseException | None, tb: TracebackType | None) -> None: ...
    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool: ...
    def __enter__(self, blocking: bool = True, timeout: float | None = None) -> bool: ...
    if sys.version_info >= (3, 9):
        def release(self, n: int = 1) -> None: ...
    else:
        def release(self) -> None: ...

class BoundedSemaphore(Semaphore): ...

class Event:
    def is_set(self) -> bool: ...
    def isSet(self) -> bool: ...  # deprecated alias for is_set()
    def set(self) -> None: ...
    def clear(self) -> None: ...
    def wait(self, timeout: float | None = None) -> bool: ...

excepthook = _excepthook
ExceptHookArgs = _ExceptHookArgs

class Timer(Thread):
    args: Iterable[Any]  # undocumented
    finished: Event  # undocumented
    function: Callable[..., Any]  # undocumented
    interval: float  # undocumented
    kwargs: Mapping[str, Any]  # undocumented

    def __init__(
        self,
        interval: float,
        function: Callable[..., object],
        args: Iterable[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
    ) -> None: ...
    def cancel(self) -> None: ...

class Barrier:
    @property
    def parties(self) -> int:
        """Return the number of threads required to trip the barrier."""
        ...
    @property
    def n_waiting(self) -> int:
        """Return the number of threads currently waiting at the barrier."""
        ...
    @property
    def broken(self) -> bool:
        """Return True if the barrier is in a broken state."""
        ...
    def __init__(self, parties: int, action: Callable[[], None] | None = None, timeout: float | None = None) -> None: ...
    def wait(self, timeout: float | None = None) -> int: ...
    def reset(self) -> None: ...
    def abort(self) -> None: ...

class BrokenBarrierError(RuntimeError): ...
