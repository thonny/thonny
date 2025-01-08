"""Support for audio filter effects

The `audiofilters` module contains classes to provide access to audio filter effects.

"""

from __future__ import annotations

from typing import Optional, Tuple

import circuitpython_typing
import synthio

class Filter:
    """A Filter effect"""

    def __init__(
        self,
        filter: Optional[synthio.Biquad | Tuple[synthio.Biquad]] = None,
        mix: synthio.BlockInput = 1.0,
        buffer_size: int = 512,
        sample_rate: int = 8000,
        bits_per_sample: int = 16,
        samples_signed: bool = True,
        channel_count: int = 1,
    ) -> None:
        """Create a Filter effect where the original sample is processed through a biquad filter
           created by a synthio.Synthesizer object. This can be used to generate a low-pass,
           high-pass, or band-pass filter.

           The mix parameter allows you to change how much of the unchanged sample passes through to
           the output to how much of the effect audio you hear as the output.

        :param Optional[synthio.Biquad|Tuple[synthio.Biquad]] filter: A normalized biquad filter object or tuple of normalized biquad filter objects. The sample is processed sequentially by each filter to produce the output samples.
        :param synthio.BlockInput mix: The mix as a ratio of the sample (0.0) to the effect (1.0).
        :param int buffer_size: The total size in bytes of each of the two playback buffers to use
        :param int sample_rate: The sample rate to be used
        :param int channel_count: The number of channels the source samples contain. 1 = mono; 2 = stereo.
        :param int bits_per_sample: The bits per sample of the effect
        :param bool samples_signed: Effect is signed (True) or unsigned (False)

        Playing adding a filter to a synth::

          import time
          import board
          import audiobusio
          import synthio
          import audiofilters

          audio = audiobusio.I2SOut(bit_clock=board.GP20, word_select=board.GP21, data=board.GP22)
          synth = synthio.Synthesizer(channel_count=1, sample_rate=44100)
          effect = audiofilters.Filter(buffer_size=1024, channel_count=1, sample_rate=44100, mix=1.0)
          effect.filter = synth.low_pass_filter(frequency=2000, Q=1.25)
          effect.play(synth)
          audio.play(effect)

          note = synthio.Note(261)
          while True:
              synth.press(note)
              time.sleep(0.25)
              synth.release(note)
              time.sleep(5)"""
        ...

    def deinit(self) -> None:
        """Deinitialises the Filter."""
        ...

    def __enter__(self) -> Filter:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    filter: synthio.Biquad | Tuple[synthio.Biquad] | None
    """A normalized biquad filter object or tuple of normalized biquad filter objects. The sample is processed sequentially by each filter to produce the output samples."""

    mix: synthio.BlockInput
    """The rate the filtered signal mix between 0 and 1 where 0 is only sample and 1 is all effect."""
    playing: bool
    """True when the effect is playing a sample. (read-only)"""
    def play(
        self, sample: circuitpython_typing.AudioSample, *, loop: bool = False
    ) -> None:
        """Plays the sample once when loop=False and continuously when loop=True.
        Does not block. Use `playing` to block.

        The sample must match the encoding settings given in the constructor."""
        ...

    def stop(self) -> None:
        """Stops playback of the sample."""
        ...
