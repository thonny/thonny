"""MIDI over USB

The `usb_midi` module contains classes to transmit and receive MIDI messages over USB."""

from __future__ import annotations

from typing import Optional, Tuple, Union

from circuitpython_typing import ReadableBuffer, WriteableBuffer

ports: Tuple[Union[PortIn, PortOut], ...]
"""Tuple of all MIDI ports. Each item is ether `PortIn` or `PortOut`."""

def disable() -> None:
    """Disable presenting a USB MIDI device to the host.
    The device is normally enabled by default, but on some boards with limited endpoints
    including ESP32-S2 and certain STM boards, it is disabled by default.
    Can be called in ``boot.py``, before USB is connected."""
    ...

def enable() -> None:
    """Enable presenting a USB MIDI device to the host.
    The device is enabled by default, so you do not normally need to call this function.
    Can be called in ``boot.py``, before USB is connected.

    If you enable too many devices at once, you will run out of USB endpoints.
    The number of available endpoints varies by microcontroller.
    CircuitPython will go into safe mode after running boot.py to inform you if
    not enough endpoints are available.
    """
    ...

def set_names(
    self,
    *,
    streaming_interface_name: Optional[str] = None,
    audio_control_interface_name: Optional[str] = None,
    in_jack_name: Optional[str] = None,
    out_jack_name: Optional[str] = None,
) -> None:
    """Override the MIDI interface names in the USB Interface Descriptor.

    :param Optional[str] streaming_interface_name: an ASCII string (or buffer) of at most 126 characters, or ``None`` to use the default name.
    :param Optional[str] audio_control_interface_name: an ASCII string (or buffer) of at most 126 characters, or ``None`` to use the default name.
    :param Optional[str] in_jack_name: an ASCII string (or buffer) of at most 126 characters, or ``None`` to use the default name.
    :param Optional[str] out_jack_name: an ASCII string (or buffer) of at most 126 characters, or ``None`` to use the default name.

    This method must be called in boot.py to have any effect.

    Not available on boards without native USB support.
    """
    ...

class PortIn:
    """Receives midi commands over USB"""

    def __init__(self) -> None:
        """You cannot create an instance of `usb_midi.PortIn`.

        PortIn objects are constructed for every corresponding entry in the USB
        descriptor and added to the ``usb_midi.ports`` tuple."""
        ...

    def read(self, nbytes: Optional[int] = None) -> Optional[bytes]:
        """Read characters.  If ``nbytes`` is specified then read at most that many
        bytes. Otherwise, read everything that arrives until the connection
        times out. Providing the number of bytes expected is highly recommended
        because it will be faster.

        :return: Data read
        :rtype: bytes or None"""
        ...

    def readinto(
        self, buf: WriteableBuffer, nbytes: Optional[int] = None
    ) -> Optional[bytes]:
        """Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: bytes or None"""
        ...

class PortOut:
    """Sends midi messages to a computer over USB"""

    def __init__(self) -> None:
        """You cannot create an instance of `usb_midi.PortOut`.

        PortOut objects are constructed for every corresponding entry in the USB
        descriptor and added to the ``usb_midi.ports`` tuple."""

    def write(self, buf: ReadableBuffer) -> Optional[int]:
        """Write the buffer of bytes to the bus.

        :return: the number of bytes written
        :rtype: int or None"""
        ...
