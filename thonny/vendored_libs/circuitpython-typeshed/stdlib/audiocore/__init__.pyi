"""Support for audio samples"""

from __future__ import annotations

import typing
from typing import Optional, Union

from circuitpython_typing import ReadableBuffer, WriteableBuffer

class RawSample:
    """A raw audio sample buffer in memory"""

    def __init__(
        self,
        buffer: ReadableBuffer,
        *,
        channel_count: int = 1,
        sample_rate: int = 8000,
        single_buffer: bool = True,
    ) -> None:
        """Create a RawSample based on the given buffer of values. If channel_count is more than
        1 then each channel's samples should alternate. In other words, for a two channel buffer, the
        first sample will be for channel 1, the second sample will be for channel two, the third for
        channel 1 and so on.

        :param ~circuitpython_typing.ReadableBuffer buffer: A buffer with samples
        :param int channel_count: The number of channels in the buffer
        :param int sample_rate: The desired playback sample rate
        :param bool single_buffer: Selects single buffered or double buffered transfer mode.  This affects
                                   what happens if the sample buffer is changed while the sample is playing.
                                   In single buffered transfers, a change in buffer contents will not affect active playback.
                                   In double buffered transfers, changed buffer contents will
                                   be played back when the transfer reaches the next half-buffer point.

        Playing 8ksps 440 Hz and 880 Hz sine waves::

          import analogbufio
          import array
          import audiocore
          import audiopwmio
          import board
          import math
          import time

          # Generate one period of sine wave.
          length = 8000 // 440
          sine_wave = array.array("h", [0] * length)
          for i in range(length):
              sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15))
          pwm = audiopwmio.PWMAudioOut(left_channel=board.D12, right_channel=board.D13)

          # Play single-buffered
          sample = audiocore.RawSample(sine_wave)
          pwm.play(sample, loop=True)
          time.sleep(3)
          # changing the wave has no effect
          for i in range(length):
               sine_wave[i] = int(math.sin(math.pi * 4 * i / length) * (2 ** 15))
          time.sleep(3)
          pwm.stop()
          time.sleep(1)

          # Play double-buffered
          sample = audiocore.RawSample(sine_wave, single_buffer=False)
          pwm.play(sample, loop=True)
          time.sleep(3)
          # changing the wave takes effect almost immediately
          for i in range(length):
              sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15))
          time.sleep(3)
          pwm.stop()
          pwm.deinit()"""
        ...

    def deinit(self) -> None:
        """Deinitialises the RawSample and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> RawSample:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    sample_rate: Optional[int]
    """32 bit value that dictates how quickly samples are played in Hertz (cycles per second).
    When the sample is looped, this can change the pitch output without changing the underlying
    sample. This will not change the sample rate of any active playback. Call ``play`` again to
    change it."""

class WaveFile:
    """Load a wave file for audio playback

    A .wav file prepped for audio playback. Only mono and stereo files are supported. Samples must
    be 8 bit unsigned or 16 bit signed. If a buffer is provided, it will be used instead of allocating
    an internal buffer, which can prevent memory fragmentation."""

    def __init__(
        self, file: Union[str, typing.BinaryIO], buffer: WriteableBuffer
    ) -> None:
        """Load a .wav file for playback with `audioio.AudioOut` or `audiobusio.I2SOut`.

        :param Union[str, typing.BinaryIO] file: The name of a wave file (preferred) or an already opened wave file
        :param ~circuitpython_typing.WriteableBuffer buffer: Optional pre-allocated buffer,
          that will be split in half and used for double-buffering of the data.
          The buffer must be 8 to 1024 bytes long.
          If not provided, two 256 byte buffers are initially allocated internally.

        Playing a wave file from flash::

          import board
          import audiocore
          import audioio
          import digitalio

          # Required for CircuitPlayground Express
          speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
          speaker_enable.switch_to_output(value=True)

          wav = audiocore.WaveFile("cplay-5.1-16bit-16khz.wav")
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(wav)
          while a.playing:
            pass
          print("stopped")
        """
        ...

    def deinit(self) -> None:
        """Deinitialises the WaveFile and releases all memory resources for reuse."""
        ...

    def __enter__(self) -> WaveFile:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    sample_rate: int
    """32 bit value that dictates how quickly samples are loaded into the DAC
    in Hertz (cycles per second). When the sample is looped, this can change
    the pitch output without changing the underlying sample."""
    bits_per_sample: int
    """Bits per sample. (read only)"""
    channel_count: int
    """Number of audio channels. (read only)"""
