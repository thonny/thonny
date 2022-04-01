"""SAMD implementation settings"""

from __future__ import annotations

from typing import Union

""":mod:`samd.clock` --- samd clock names
--------------------------------------------------------

.. module:: samd.clock
  :synopsis: samd clock names
  :platform: SAMD21

References to clocks as named by the microcontroller"""

class Clock:
    """Identifies a clock on the microcontroller.

    They are fixed by the hardware so they cannot be constructed on demand. Instead, use
    ``samd.clock`` to reference the desired clock."""

    enabled: bool
    """Is the clock enabled? (read-only)"""

    parent: Union[Clock, None]
    """Clock parent. (read-only)"""

    frequency: int
    """Clock frequency in Herz. (read-only)"""

    calibration: int
    """Clock calibration. Not all clocks can be calibrated."""
