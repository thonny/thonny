"""Supervisor settings"""

from __future__ import annotations

from typing import Optional

runtime: Runtime
"""Runtime information, such as ``runtime.serial_connected``
(USB serial connection status).
This object is the sole instance of `supervisor.Runtime`."""

def enable_autoreload() -> None:
    """Enable autoreload based on USB file write activity."""
    ...

def disable_autoreload() -> None:
    """Disable autoreload based on USB file write activity until
    `enable_autoreload` is called."""
    ...

def set_rgb_status_brightness(brightness: int) -> None:
    """Set brightness of status RGB LED from 0-255. This will take effect
    after the current code finishes and the status LED is used to show
    the finish state."""
    ...

def reload() -> None:
    """Reload the main Python code and run it (equivalent to hitting Ctrl-D at the REPL)."""
    ...

def set_next_stack_limit(size: int) -> None:
    """Set the size of the stack for the next vm run. If its too large, the default will be used."""
    ...

def set_next_code_file(
    filename: Optional[str],
    *,
    reload_on_success: bool = False,
    reload_on_error: bool = False,
    sticky_on_success: bool = False,
    sticky_on_error: bool = False,
    sticky_on_reload: bool = False,
) -> None:
    """Set what file to run on the next vm run.

    When not ``None``, the given ``filename`` is inserted at the front of the usual ['code.py',
    'main.py'] search sequence.

    The optional keyword arguments specify what happens after the specified file has run:

    ``sticky_on_…`` determine whether the newly set filename and options stay in effect: If
    True, further runs will continue to run that file (unless it says otherwise by calling
    ``set_next_code_filename()`` itself). If False, the settings will only affect one run and
    revert to the standard code.py/main.py afterwards.

    ``reload_on_…`` determine how to continue: If False, wait in the usual "Code done running.
    Waiting for reload. / Press any key to enter the REPL. Use CTRL-D to reload." state. If
    True, reload immediately as if CTRL-D was pressed.

    ``…_on_success`` take effect when the program runs to completion or calls ``sys.exit()``.

    ``…_on_error`` take effect when the program exits with an exception, including the
    KeyboardInterrupt caused by CTRL-C.

    ``…_on_reload`` take effect when the program is interrupted by files being written to the USB
    drive (auto-reload) or when it calls ``supervisor.reload()``.

    These settings are stored in RAM, not in persistent memory, and will therefore only affect
    soft reloads. Powering off or resetting the device will always revert to standard settings.

    When called multiple times in the same run, only the last call takes effect, replacing any
    settings made by previous ones. This is the main use of passing ``None`` as a filename: to
    reset to the standard search sequence."""
    ...

def ticks_ms() -> int:
    """Return the time in milliseconds since an unspecified reference point, wrapping after 2**29ms.

    The value is initialized so that the first overflow occurs about 65
    seconds after power-on, making it feasible to check that your program
    works properly around an overflow.

    The wrap value was chosen so that it is always possible to add
    or subtract two `ticks_ms` values without overflow on a board without
    long ints (or without allocating any long integer objects, on boards with
    long ints).

    This ticks value comes from a low-accuracy clock internal to the
    microcontroller, just like `time.monotonic`.  Due to its low accuracy
    and the fact that it "wraps around" every few days, it is intended
    for working with short term events like advancing an LED animation,
    not for long term events like counting down the time until a holiday.

    Addition, subtraction, and comparison of ticks values can be done
    with routines like the following::

        _TICKS_PERIOD = const(1<<29)
        _TICKS_MAX = const(_TICKS_PERIOD-1)
        _TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

        def ticks_add(ticks, delta):
            "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
            return (a + b) % _TICKS_PERIOD

        def ticks_diff(ticks1, ticks2):
            "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
            diff = (ticks1 - ticks2) & _TICKS_MAX
            diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
            return diff

        def ticks_less(ticks1, ticks2):
            "Return true iff ticks1 is less than ticks2, assuming that they are within 2**28 ticks"
            return ticks_diff(ticks1, ticks2) < 0

    """
    ...

def get_previous_traceback() -> Optional[str]:
    """If the last vm run ended with an exception (including the KeyboardInterrupt caused by
    CTRL-C), returns the traceback as a string.
    Otherwise, returns ``None``.

    An exception traceback is only preserved over a soft reload, a hard reset clears it.

    Only code (main or boot) runs are considered, not REPL runs."""
    ...

def disable_ble_workflow() -> None:
    """Disable ble workflow until a reset. This prevents BLE advertising outside of the VM and
    the services used for it."""
    ...

def reset_terminal(x_pixels: int, y_pixels: int) -> None:
    """Reset the CircuitPython serial terminal with new dimensions."""
    ...

class RunReason:
    """The reason that CircuitPython started running."""

    STARTUP: object
    """CircuitPython started the microcontroller started up. See `microcontroller.Processor.reset_reason`
       for more detail on why the microcontroller was started."""

    AUTO_RELOAD: object
    """CircuitPython restarted due to an external write to the filesystem."""

    SUPERVISOR_RELOAD: object
    """CircuitPython restarted due to a call to `supervisor.reload()`."""

    REPL_RELOAD: object
    """CircuitPython started due to the user typing CTRL-D in the REPL."""

class Runtime:
    """Current status of runtime objects.

    Usage::

       import supervisor
       if supervisor.runtime.serial_connected:
           print("Hello World!")"""

    def __init__(self) -> None:
        """You cannot create an instance of `supervisor.Runtime`.
        Use `supervisor.runtime` to access the sole instance available."""
        ...
    usb_connected: bool
    """Returns the USB enumeration status (read-only)."""

    serial_connected: bool
    """Returns the USB serial communication status (read-only)."""

    serial_bytes_available: int
    """Returns the whether any bytes are available to read
    on the USB serial input.  Allows for polling to see whether
    to call the built-in input() or wait. (read-only)"""

    run_reason: RunReason
    """Returns why CircuitPython started running this particular time."""
