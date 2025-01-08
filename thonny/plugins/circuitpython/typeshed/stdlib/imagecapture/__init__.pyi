"""Support for "Parallel capture" interfaces

.. seealso::

    Espressif microcontrollers use the `espcamera` module together.

"""

from __future__ import annotations

from typing import List, Optional

import microcontroller
from circuitpython_typing import WriteableBuffer

class ParallelImageCapture:
    """Capture image frames from a camera with parallel data interface"""

    def __init__(
        self,
        *,
        data_pins: List[microcontroller.Pin],
        clock: microcontroller.Pin,
        vsync: Optional[microcontroller.Pin],
        href: Optional[microcontroller.Pin],
    ) -> None:
        """Create a parallel image capture object

        This object is usually used with a camera-specific wrapper library such as `adafruit_ov5640 <https://circuitpython.readthedocs.io/projects/ov5640/en/latest/>`_.

        :param List[microcontroller.Pin] data_pins: The data pins.
        :param microcontroller.Pin clock: The pixel clock input.
        :param microcontroller.Pin vsync: The vertical sync input, which has a negative-going pulse at the beginning of each frame.
        :param microcontroller.Pin href: The horizontal reference input, which is high whenever the camera is transmitting valid pixel information.
        """
        ...

    def capture(self, buffer: WriteableBuffer) -> WriteableBuffer:
        """Capture a single frame into the given buffer.

        This will stop a continuous-mode capture, if one is in progress."""
        ...

    def continuous_capture_start(
        self, buffer1: WriteableBuffer, buffer2: WriteableBuffer, /
    ) -> None:
        """Begin capturing into the given buffers in the background.

        Call `continuous_capture_get_frame` to get the next available
        frame, and `continuous_capture_stop` to stop capturing.

        Until `continuous_capture_stop` (or `deinit`) is called, the
        `ParallelImageCapture` object keeps references to ``buffer1`` and
        ``buffer2``, so the objects will not be garbage collected."""
        ...

    def continuous_capture_get_frame(self) -> WriteableBuffer:
        """Return the next available frame, one of the two buffers passed to `continuous_capture_start`"""
        ...

    def continuous_capture_stop(self) -> None:
        """Stop continuous capture.

        Calling this method also causes the object to release its
        references to the buffers passed to `continuous_capture_start`,
        potentially allowing the objects to be garbage collected."""
        ...

    def deinit(self) -> None:
        """Deinitialize this instance"""
        ...

    def __enter__(self) -> ParallelImageCapture:
        """No-op used in Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware on context exit. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
