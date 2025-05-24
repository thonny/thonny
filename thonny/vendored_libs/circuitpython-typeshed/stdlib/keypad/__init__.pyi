"""Support for scanning keys and key matrices

The `keypad` module provides native support to scan sets of keys or buttons,
connected independently to individual pins,
connected to a shift register,
or connected in a row-and-column matrix.

For more information about working with the `keypad` module in CircuitPython,
see `this Learn guide <https://learn.adafruit.com/key-pad-matrix-scanning-in-circuitpython>`_.

.. warning:: Using pull-downs with `keypad` on Raspberry Pi RP2350 A2 stepping has some limitations
   due to a GPIO hardware issue that causes excessive leakage current (~120uA).
   A pin can read as high even when driven or pulled low, if the input signal is high
   impedance or if an attached pull-down resistor is too weak (has too high a value).
   See the warning in `digitalio` for more information.

.. jinja
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union

import microcontroller

class Event:
    """A key transition event."""

    def __init__(
        self, key_number: int = 0, pressed: bool = True, timestamp: Optional[int] = None
    ) -> None:
        """Create a key transition event, which reports a key-pressed or key-released transition.

        :param int key_number: The key number.
        :param bool pressed: ``True`` if the key was pressed; ``False`` if it was released.
        :param int timestamp: The time in milliseconds that the keypress occurred in the `supervisor.ticks_ms` time system.  If specified as None, the current value of `supervisor.ticks_ms` is used.
        """
        ...
    key_number: int
    """The key number."""
    pressed: bool
    """``True`` if the event represents a key down (pressed) transition.
    The opposite of `released`.
    """
    released: bool
    """``True`` if the event represents a key up (released) transition.
    The opposite of `pressed`.
    """
    timestamp: int
    """The timestamp."""

    def __eq__(self, other: object) -> bool:
        """Two `Event` objects are equal if their `key_number`
        and `pressed`/`released` values are equal.
        Note that this does not compare the event timestamps.
        """
        ...

    def __hash__(self) -> int:
        """Returns a hash for the `Event`, so it can be used in dictionaries, etc..

        Note that as events with different timestamps compare equal, they also hash to the same value.
        """
        ...

class EventQueue:
    """A queue of `Event` objects, filled by a `keypad` scanner such as `Keys` or `KeyMatrix`.

    You cannot create an instance of `EventQueue` directly. Each scanner creates an
    instance when it is created.
    """

    ...

    def get(self) -> Optional[Event]:
        """Remove the next key transition event from the `EventQueue` and return it.
        Return ``None`` if no events are pending.

        Note that the queue size is limited; see ``max_events`` in the constructor of
        a scanner such as `Keys` or `KeyMatrix`.
        If a new event arrives when the queue is full, the event is discarded, and
        `overflowed` is set to ``True``.

        :return: The next queued key transition `Event`.
        :rtype: Optional[Event]
        """
        ...

    def get_into(self, event: Event) -> bool:
        """Remove the next key transition event from the ``EventQueue`, store it in ``event``,
        and return ``True``.
        If there are no queued events, do not touch ``event`` and return ``False``.

        The advantage of this method over ``get()`` is that it does not allocate storage.
        Instead you can reuse an existing ``Event`` object.

        Note that the queue size is limited; see ``max_events`` in the constructor of
        a scanner such as `Keys` or `KeyMatrix`.

        :return: ``True`` if an event was available and stored, ``False`` if not.
        :rtype: bool
        """
        ...

    def clear(self) -> None:
        """Clear any queued key transition events. Also sets `overflowed` to ``False``."""
        ...

    def __bool__(self) -> bool:
        """``True`` if `len()` is greater than zero.
        This is an easy way to check if the queue is empty.
        """
        ...

    def __len__(self) -> int:
        """Return the number of events currently in the queue. Used to implement ``len()``."""
        ...
    overflowed: bool
    """``True`` if an event could not be added to the event queue because it was full. (read-only)
    Set to ``False`` by  `clear()`.
    """

class KeyMatrix:
    """Manage a 2D matrix of keys with row and column pins.

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["keypad.KeyMatrix"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    """

    def __init__(
        self,
        row_pins: Sequence[microcontroller.Pin],
        column_pins: Sequence[microcontroller.Pin],
        columns_to_anodes: bool = True,
        interval: float = 0.020,
        max_events: int = 64,
        debounce_threshold: int = 1,
    ) -> None:
        """
        Create a `Keys` object that will scan the key matrix attached to the given row and column pins.
        There should not be any external pull-ups or pull-downs on the matrix:
        ``KeyMatrix`` enables internal pull-ups or pull-downs on the pins as necessary.

        The keys are numbered sequentially from zero. A key number can be computed
        by ``row * len(column_pins) + column``.

        An `EventQueue` is created when this object is created and is available in the `events` attribute.

        :param Sequence[microcontroller.Pin] row_pins: The pins attached to the rows.
        :param Sequence[microcontroller.Pin] column_pins: The pins attached to the columns.
        :param bool columns_to_anodes: Default ``True``.
          If the matrix uses diodes, the diode anodes are typically connected to the column pins,
          and the cathodes should be connected to the row pins. If your diodes are reversed,
          set ``columns_to_anodes`` to ``False``.
        :param float interval: Scan keys no more often than ``interval`` to allow for debouncing.
          ``interval`` is in float seconds. The default is 0.020 (20 msecs).
        :param int max_events: maximum size of `events` `EventQueue`:
          maximum number of key transition events that are saved.
          Must be >= 1.
          If a new event arrives when the queue is full, the oldest event is discarded.
        :param int debounce_threshold: Emit events for state changes only after a key has been
          in the respective state for ``debounce_threshold`` times on average.
          Successive measurements are spaced apart by ``interval`` seconds.
          The default is 1, which resolves immediately. The maximum is 127.
        """
        ...

    def deinit(self) -> None:
        """Stop scanning and release the pins."""
        ...

    def __enter__(self) -> KeyMatrix:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def reset(self) -> None:
        """Reset the internal state of the scanner to assume that all keys are now released.
        Any key that is already pressed at the time of this call will therefore immediately cause
        a new key-pressed event to occur.
        For instance, if you call `reset()` immediately after creating a `KeyMatrix` object
        at the beginning of your program, the events it generates will let you determine which keys
        were being held down at program start.
        """
        ...
    key_count: int
    """The number of keys that are being scanned. (read-only)
    """

    def key_number_to_row_column(self, key_number: int) -> Tuple[int]:
        """Return the row and column for the given key number.
        The row is ``key_number // len(column_pins)``.
        The column is ``key_number % len(column_pins)``.

        :return: ``(row, column)``
        :rtype: Tuple[int]
        """
        ...

    def row_column_to_key_number(self, row: int, column: int) -> int:
        """Return the key number for a given row and column.
        The key number is ``row * len(column_pins) + column``.
        """
        ...
    events: EventQueue
    """The `EventQueue` associated with this `Keys` object. (read-only)
    """

class Keys:
    """Manage a set of independent keys.

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["keypad.Keys"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    """

    def __init__(
        self,
        pins: Sequence[microcontroller.Pin],
        *,
        value_when_pressed: bool,
        pull: bool = True,
        interval: float = 0.020,
        max_events: int = 64,
        debounce_threshold: int = 1,
    ) -> None:
        """
        Create a `Keys` object that will scan keys attached to the given sequence of pins.
        Each key is independent and attached to its own pin.

        An `EventQueue` is created when this object is created and is available in the `events` attribute.

        :param Sequence[microcontroller.Pin] pins: The pins attached to the keys.
          The key numbers correspond to indices into this sequence.
        :param bool value_when_pressed: ``True`` if the pin reads high when the key is pressed.
          ``False`` if the pin reads low (is grounded) when the key is pressed.
          All the pins must be connected in the same way.
        :param bool pull: ``True`` if an internal pull-up or pull-down should be
          enabled on each pin. A pull-up will be used if ``value_when_pressed`` is ``False``;
          a pull-down will be used if it is ``True``.
          If an external pull is already provided for all the pins, you can set ``pull`` to ``False``.
          However, enabling an internal pull when an external one is already present is not a problem;
          it simply uses slightly more current.
        :param float interval: Scan keys no more often than ``interval`` to allow for debouncing.
          ``interval`` is in float seconds. The default is 0.020 (20 msecs).
        :param int max_events: maximum size of `events` `EventQueue`:
          maximum number of key transition events that are saved.
          Must be >= 1.
          If a new event arrives when the queue is full, the oldest event is discarded.
        :param int debounce_threshold: Emit events for state changes only after a key has been
          in the respective state for ``debounce_threshold`` times on average.
          Successive measurements are spaced apart by ``interval`` seconds.
          The default is 1, which resolves immediately. The maximum is 127.
        """
        ...

    def deinit(self) -> None:
        """Stop scanning and release the pins."""
        ...

    def __enter__(self) -> Keys:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def reset(self) -> None:
        """Reset the internal state of the scanner to assume that all keys are now released.
        Any key that is already pressed at the time of this call will therefore immediately cause
        a new key-pressed event to occur.
        For instance, if you call `reset()` immediately after creating a `Keys` object
        at the beginning of your program, the events it generates will let you determine which keys
        were being held down at program start.
        """
        ...
    key_count: int
    """The number of keys that are being scanned. (read-only)
    """
    events: EventQueue
    """The `EventQueue` associated with this `Keys` object. (read-only)
    """

class ShiftRegisterKeys:
    """Manage a set of keys attached to an incoming shift register.

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["keypad.ShiftRegisterKeys"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    """

    def __init__(
        self,
        *,
        clock: microcontroller.Pin,
        data: Union[microcontroller.Pin, Sequence[microcontroller.Pin]],
        latch: microcontroller.Pin,
        value_to_latch: bool = True,
        key_count: Union[int, Sequence[int]],
        value_when_pressed: bool,
        interval: float = 0.020,
        max_events: int = 64,
        debounce_threshold: int = 1,
    ) -> None:
        """
        Create a `Keys` object that will scan keys attached to a parallel-in serial-out shift register
        like the 74HC165 or CD4021.
        Note that you may chain shift registers to load in as many values as you need.
        Furthermore, you can put multiple shift registers in parallel and share clock and latch.

        Key number 0 is the first (or more properly, the zero-th) bit read. In the
        74HC165, this bit is labeled ``Q7``. Key number 1 will be the value of ``Q6``, etc.
        Key numbers are sequenced such that there are ``key_count[0]`` values read from ``data[0]``, followed by ``key_count[1]`` values read from ``data[1]``, etc.

        An `EventQueue` is created when this object is created and is available in the `events` attribute.

        :param microcontroller.Pin clock: The shift register clock pin.
          The shift register should clock on a low-to-high transition.
        :param Union[microcontroller.Pin, Sequence[microcontroller.Pin]] data: the incoming shift register data pin(s).
          When a ``microcontroller.Pin`` argument is given, it is logically equivalent to a one-element sequence.
        :param microcontroller.Pin latch:
          Pin used to latch parallel data going into the shift register.
        :param bool value_to_latch: Pin state to latch data being read.
          ``True`` if the data is latched when ``latch`` goes high
          ``False`` if the data is latched when ``latch`` goes low.
          The default is ``True``, which is how the 74HC165 operates. The CD4021 latch is the opposite.
          Once the data is latched, it will be shifted out by toggling the clock pin.
        :param Union[int, Sequence[int]] key_count: number of data lines to clock in (per data pin)
          When an ``int`` argument is given, it is logically equivalent to a one-element sequence.
        :param bool value_when_pressed: ``True`` if the pin reads high when the key is pressed.
          ``False`` if the pin reads low (is grounded) when the key is pressed.
        :param float interval: Scan keys no more often than ``interval`` to allow for debouncing.
          ``interval`` is in float seconds. The default is 0.020 (20 msecs).
        :param int max_events: maximum size of `events` `EventQueue`:
          maximum number of key transition events that are saved.
          Must be >= 1.
          If a new event arrives when the queue is full, the oldest event is discarded.
        :param int debounce_threshold: Emit events for state changes only after a key has been
          in the respective state for ``debounce_threshold`` times on average.
          Successive measurements are spaced apart by ``interval`` seconds.
          The default is 1, which resolves immediately. The maximum is 127.
        """
        ...

    def deinit(self) -> None:
        """Stop scanning and release the pins."""
        ...

    def __enter__(self) -> Keys:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def reset(self) -> None:
        """Reset the internal state of the scanner to assume that all keys are now released.
        Any key that is already pressed at the time of this call will therefore immediately cause
        a new key-pressed event to occur.
        For instance, if you call `reset()` immediately after creating a `ShiftRegisterKeys` object
        at the beginning of your program, the events it generates will let you determine which keys
        were being held down at program start.
        """
        ...
    key_count: int
    """The total number of keys that are being scanned. (read-only)
    """
    events: EventQueue
    """The `EventQueue` associated with this `Keys` object. (read-only)
    """
