"""Support for MP3-compressed audio files

For more information about working with MP3 files in CircuitPython,
see `this CircuitPython Essentials Learn guide page
<https://learn.adafruit.com/circuitpython-essentials/circuitpython-mp3-audio>`_.
"""

from __future__ import annotations

import typing
from typing import Union

from circuitpython_typing import WriteableBuffer

class MP3Decoder:
    """Load a mp3 file for audio playback

    .. note::

        ``MP3Decoder`` uses a lot of contiguous memory, so care should be given to
        optimizing memory usage.  More information and recommendations can be found here:
        https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython/reducing-memory-fragmentation
    """

    def __init__(
        self, file: Union[str, typing.BinaryIO], buffer: WriteableBuffer
    ) -> None:
        """Load a .mp3 file for playback with `audioio.AudioOut` or `audiobusio.I2SOut`.

        :param Union[str, typing.BinaryIO] file: The name of a mp3 file (preferred) or an already opened mp3 file
        :param ~circuitpython_typing.WriteableBuffer buffer: Optional pre-allocated buffer, that will be split and used for buffering the data. The buffer is split into two parts for decoded data and the remainder is used for pre-decoded data. When playing from a socket, a larger buffer can help reduce playback glitches at the expense of increased memory usage.

        Playback of mp3 audio is CPU intensive, and the
        exact limit depends on many factors such as the particular
        microcontroller, SD card or flash performance, network performance, and
        other code in use such as displayio. If playback is garbled, skips, or plays as
        static, first try using a "simpler" mp3:

          * Use constant bit rate (CBR) not VBR or ABR (variable or average bit rate) when encoding your mp3 file
          * Use a lower sample rate (e.g., 11.025kHz instead of 48kHz)
          * Use a lower bit rate (e.g., 32kbit/s instead of 256kbit/s)

        Reduce activity taking place at the same time as
        mp3 playback. For instance, only update small portions of a
        displayio screen if audio is playing. Disable auto-refresh
        and explicitly call refresh.

        Playing a mp3 file from flash::

          import board
          import audiomp3
          import audioio
          import digitalio

          # Required for CircuitPlayground Express
          speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
          speaker_enable.switch_to_output(value=True)

          mp3 = audiomp3.MP3Decoder("cplay-16bit-16khz-64kbps.mp3")
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(mp3)
          while a.playing:
            pass
          print("stopped")

        It is possible to seek within a file before playing it::

            with open("/test.mp3", "rb") as stream:
                stream.seek(128000 * 30 // 8) # Seek about 30s into a 128kbit/s stream
                decoder.file = stream

        If the stream is played with ``loop = True``, the loop will start at the beginning.

        It is possible to stream an mp3 from a socket, including a secure socket.
        The MP3Decoder may change the timeout and non-blocking status of the socket.
        Using a larger decode buffer with a stream can be helpful to avoid data underruns.
        An ``adafruit_requests`` request must be made with ``headers={"Connection": "close"}`` so
        that the socket closes when the stream ends.
        """
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
    def open(self, filepath: str) -> None:
        """Takes in the name of a mp3 file, opens it, and replaces the old playback file."""
        ...
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
