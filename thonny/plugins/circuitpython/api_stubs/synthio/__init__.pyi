"""Support for MIDI synthesis"""

from __future__ import annotations

import typing
from typing import Optional

from circuitpython_typing import ReadableBuffer

def from_file(file: typing.BinaryIO, *, sample_rate: int = 11025) -> MidiTrack:
    """Create an AudioSample from an already opened MIDI file.
    Currently, only single-track MIDI (type 0) is supported.

    :param typing.BinaryIO file: Already opened MIDI file
    :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory


    Playing a MIDI file from flash::

          import audioio
          import board
          import synthio

          data = open("single-track.midi", "rb")
          midi = synthio.from_file(data)
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(midi)
          while a.playing:
            pass
          print("stopped")"""
    ...

class MidiTrack:
    """Simple square-wave MIDI synth"""

    def __init__(
        self, buffer: ReadableBuffer, tempo: int, *, sample_rate: int = 11025
    ) -> None:
        """Create a MidiTrack from the given stream of MIDI events. Only "Note On" and "Note Off" events
        are supported; channel numbers and key velocities are ignored. Up to two notes may be on at the
        same time.

        :param ~circuitpython_typing.ReadableBuffer buffer: Stream of MIDI events, as stored in a MIDI file track chunk
        :param int tempo: Tempo of the streamed events, in MIDI ticks per second
        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory

        Simple melody::

          import audioio
          import board
          import synthio

          dac = audioio.AudioOut(board.SPEAKER)
          melody = synthio.MidiTrack(b"\\0\\x90H\\0*\\x80H\\0\\6\\x90J\\0*\\x80J\\0\\6\\x90L\\0*\\x80L\\0\\6\\x90J\\0" +
                                     b"*\\x80J\\0\\6\\x90H\\0*\\x80H\\0\\6\\x90J\\0*\\x80J\\0\\6\\x90L\\0T\\x80L\\0" +
                                     b"\\x0c\\x90H\\0T\\x80H\\0\\x0c\\x90H\\0T\\x80H\\0", tempo=640)
          dac.play(melody)
          print("playing")
          while dac.playing:
            pass
          print("stopped")"""
        ...
    def deinit(self) -> None:
        """Deinitialises the MidiTrack and releases any hardware resources for reuse."""
        ...
    def __enter__(self) -> MidiTrack:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    sample_rate: Optional[int]
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""
