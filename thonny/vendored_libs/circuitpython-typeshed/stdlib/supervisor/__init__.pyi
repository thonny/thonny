"""Supervisor settings"""

from __future__ import annotations

from typing import Optional

import displayio

runtime: Runtime
"""Runtime information, such as ``runtime.serial_connected``
(USB serial connection status).
This object is the sole instance of `supervisor.Runtime`."""
status_bar: StatusBar
"""The status bar, shown on an attached display, and also sent to
an attached terminal via OSC escape codes over the REPL serial connection.
The status bar reports the current IP or BLE connection, what file is running,
the last exception name and location, and firmware version information.
This object is the sole instance of `supervisor.StatusBar`."""

def reload() -> None:
    """Reload the main Python code and run it (equivalent to hitting Ctrl-D at the REPL)."""
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
            return (ticks + delta) % _TICKS_PERIOD

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

def reset_terminal(x_pixels: int, y_pixels: int) -> None:
    """Reset the CircuitPython serial terminal with new dimensions."""
    ...

def set_usb_identification(
    manufacturer: Optional[str] = None,
    product: Optional[str] = None,
    vid: int = -1,
    pid: int = -1,
) -> None:
    """Override identification constants in the USB Device Descriptor.

    If passed, `manufacturer` and `product` must be ASCII strings (or buffers) of at most 126
    characters. Any omitted arguments will be left at their default values.

    This method must be called in boot.py to have any effect.

    Not available on boards without native USB support.
    """
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
    """Returns the number of bytes are available to read on the console serial input.
    Multiple console serial inputs may be in use at once, including
    USB, web workflow, BLE workflow, and/or UART.

    Allows for polling to see whether to call the built-in input() or wait. (read-only)

    **Limitations**: On STM, UART (not USB) console input can only determine that at least one character
    is available, and so if only the UART console is in use, only ``1`` or ``0`` will be returned.

    Changed in version 9.1.0: Previously returned only ``True`` or ``False``.
    Since ``0`` acts as ``False``, ``if supervisor.runtime.serial_byes_available:``
    will still work.
    """
    run_reason: RunReason
    """Why CircuitPython started running this particular time (read-only)."""
    safe_mode_reason: SafeModeReason
    """Why CircuitPython went into safe mode this particular time (read-only).

    **Limitations**: Raises ``NotImplementedError`` on builds that do not implement ``safemode.py``.
    """
    autoreload: bool
    """Whether CircuitPython may autoreload based on workflow writes to the filesystem."""

    ble_workflow: bool
    """Enable/Disable ble workflow until a reset. This prevents BLE advertising outside of the VM and
    the services used for it."""

    rgb_status_brightness: int
    """Set brightness of status RGB LED from 0-255. This will take effect
    after the current code finishes and the status LED is used to show
    the finish state."""

    display: displayio.AnyDisplay | None
    """The primary configured displayio display, if any.

    If the board has a display that is hard coded, or that was explicitly set
    in boot.py or code.py (including a previous run of code.py), it is
    available here until it is released with ``displayio.release_displays()``.

    The display can be of any supported display type, such as `busdisplay.BusDisplay`.

    If no display is configured, this property is `None`.

    In a future release of CircuitPython, any display that is not the primary display
    will be automatically released at the end of running a code file.

    On boards without displayio, this property is present but the value is always `None`."""

class SafeModeReason:
    """The reason that CircuitPython went into safe mode.

    **Limitations**: Class not available on builds that do not implement ``safemode.py``.
    """

    NONE: object
    """CircuitPython is not in safe mode."""

    BROWNOUT: object
    """The microcontroller voltage dropped too low."""

    FLASH_WRITE_FAIL: object
    """Could not write to flash memory."""

    GC_ALLOC_OUTSIDE_VM: object
    """CircuitPython tried to allocate storage when its virtual machine was not running."""

    HARD_FAULT: object
    """The microcontroller detected a fault, such as an out-of-bounds memory write."""

    INTERRUPT_ERROR: object
    """Internal error related to interrupts."""

    NLR_JUMP_FAIL: object
    """An error occurred during exception handling, possibly due to memory corruption."""

    NO_CIRCUITPY: object
    """The CIRCUITPY drive was not available."""

    NO_HEAP: object
    """Heap storage was not present."""

    PROGRAMMATIC: object
    """The program entered safe mode using the `supervisor` module."""

    SDK_FATAL_ERROR: object
    """Third party firmware reported a fatal error."""

    STACK_OVERFLOW: object
    """The CircuitPython heap was corrupted because the stack was too small."""

    USB_BOOT_DEVICE_NOT_INTERFACE_ZERO: object
    """The USB HID boot device was not set up to be the first device, on interface #0."""

    USB_TOO_MANY_ENDPOINTS: object
    """USB devices need more endpoints than are available."""

    USB_TOO_MANY_INTERFACE_NAMES: object
    """USB devices specify too many interface names."""

    USER: object
    """The user pressed one or more buttons to enter safe mode.
    This safe mode does **not** cause ``safemode.py`` to be run, since its purpose
    is to prevent all user code from running.
    This allows errors in ``safemode.py`` to be corrected easily.
    """

    WATCHDOG: object
    """An internal watchdog timer expired."""

class StatusBar:
    """Current status of runtime objects.

    Usage::

       import supervisor

       supervisor.status_bar.console = False
    """

    def __init__(self) -> None:
        """You cannot create an instance of `supervisor.StatusBar`.
        Use `supervisor.status_bar` to access the sole instance available."""
        ...
    console: bool
    """Whether status bar information is sent over the console (REPL) serial connection,
    using OSC terminal escape codes that change the terminal's title. Default is ``True``.
    If set to ``False``, status bar will be cleared and then disabled.
    May be set in ``boot.py`` or later. Persists across soft restarts.
    """
    display: bool
    """Whether status bar information is displayed on the top line of the display.
    Default is ``True``. If set to ``False``, status bar will be cleared and then disabled.
    May be set in ``boot.py`` or later.  Persists across soft restarts.
    Not available if `terminalio` is not available.
    """
