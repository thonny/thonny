"""Support for MP3-compressed audio files"""

from __future__ import annotations

import typing

from circuitpython_typing import WriteableBuffer

class MP3Decoder:
    """Load a mp3 file for audio playback"""

    def __init__(self, file: typing.BinaryIO, buffer: WriteableBuffer) -> None:

        """Load a .mp3 file for playback with `audioio.AudioOut` or `audiobusio.I2SOut`.

        :param typing.BinaryIO file: Already opened mp3 file
        :param ~circuitpython_typing.WriteableBuffer buffer: Optional pre-allocated buffer, that will be split in half and used for double-buffering of the data. If not provided, two buffers are allocated internally.  The specific buffer size required depends on the mp3 file.


        Playing a mp3 file from flash::

          import board
          import audiomp3
          import audioio
          import digitalio

          # Required for CircuitPlayground Express
          speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
          speaker_enable.switch_to_output(value=True)

          data = open("cplay-16bit-16khz-64kbps.mp3", "rb")
          mp3 = audiomp3.MP3Decoder(data)
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(mp3)
          while a.playing:
            pass
          print("stopped")"""
        ...
    def deinit(self) -> None:
        """Deinitialises the MP3 and releases all memory resources for reuse."""
        ...
    def __enter__(self) -> MP3Decoder:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    file: typing.BinaryIO
    """File to play back."""

    sample_rate: int
    """32 bit value that dictates how quickly samples are loaded into the DAC
    in Hertz (cycles per second). When the sample is looped, this can change
    the pitch output without changing the underlying sample."""

    bits_per_sample: int
    """Bits per sample. (read only)"""

    channel_count: int
    """Number of audio channels. (read only)"""

    rms_level: float
    """The RMS audio level of a recently played moment of audio. (read only)"""

    samples_decoded: int
    """The number of audio samples decoded from the current file. (read only)"""
