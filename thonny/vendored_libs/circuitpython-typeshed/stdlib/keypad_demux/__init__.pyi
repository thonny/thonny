"""Support for scanning key matrices that use a demultiplexer

The `keypad_demux` module provides native support to scan a matrix of keys or buttons
where either the row or column axis is controlled by a demultiplexer or decoder IC
such as the 74LS138 or 74LS238.  In this arrangement a binary input value
determines which column (or row) to select, thereby reducing the number of input pins.
For example the input 101 would select line 5 in the matrix.
Set ``columns_to_anodes`` to ``False`` with a non-inverting demultiplexer
which drives the selected line high.
Set ``transpose`` to ``True`` if columns are multiplexed rather than rows.

.. jinja
"""

from __future__ import annotations

from typing import Sequence, Tuple

import keypad
import microcontroller

class DemuxKeyMatrix:
    """Manage Cardputer 2D matrix of keys with a demultiplexer to drive rows and pins on columns.

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["keypad_demux.DemuxKeyMatrix"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    """

    def __init__(
        self,
        row_addr_pins: Sequence[microcontroller.Pin],
        column_pins: Sequence[microcontroller.Pin],
        columns_to_anodes: bool = True,
        transpose: bool = False,
        interval: float = 0.020,
        max_events: int = 64,
        debounce_threshold: int = 1,
    ) -> None:
        """
        Create a `keypad.Keys` object that will scan the key matrix attached to the given row and column pins.
        There should not be any external pull-ups or pull-downs on the matrix:
        ``DemuxKeyMatrix`` enables internal pull-ups or pull-downs on the pins as necessary.

        The keys are numbered sequentially from zero. A key number can be computed
        by ``row * len(column_pins) + column``.

        An `keypad.EventQueue` is created when this object is created and is available in the `events` attribute.

        :param Sequence[microcontroller.Pin] row_addr_pins: The pins attached to the rows demultiplexer.
          If your columns are multiplexed, set ``transpose`` to ``True``.
        :param Sequence[microcontroller.Pin] column_pins: The pins attached to the columns.
        :param bool columns_to_anodes: Default ``True``.
          If the matrix uses diodes, the diode anodes are typically connected to the column pins
          with the cathodes connected to the row pins.  This implies an inverting multiplexer that drives
          the selected row pin low.  If your diodes are reversed, with a non-inverting multiplexer
          that drives the selected row high, set ``columns_to_anodes`` to ``False``.
          If ``transpose`` is ``True`` the sense of columns and rows are reversed here.
        :param bool transpose: Default ``False``.
          If your matrix is multiplexed on columns rather than rows, set ``transpose`` to ``True``.
          This swaps the meaning of ``row_addr_pins`` to ``column_addr_pins``;
          ``column_pins`` to ``row_pins``; and ``columns_to_anodes`` to ``rows_to_anodes``.
        :param float interval: Scan keys no more often than ``interval`` to allow for debouncing.
          ``interval`` is in float seconds. The default is 0.020 (20 msecs).
        :param int max_events: maximum size of `events` `keypad.EventQueue`:
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

    def __enter__(self) -> DemuxKeyMatrix:
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
        For instance, if you call `reset()` immediately after creating a `DemuxKeyMatrix` object
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
    events: keypad.EventQueue
    """The `keypad.EventQueue` associated with this `keypad.Keys` object. (read-only)
    """
