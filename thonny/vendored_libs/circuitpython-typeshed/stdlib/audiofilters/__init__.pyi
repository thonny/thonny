"""Support for audio filter effects

The `audiofilters` module contains classes to provide access to audio filter effects.

"""

from __future__ import annotations

from typing import Optional, Tuple

import circuitpython_typing
import synthio

class DistortionMode:
    """The method of distortion used by the `audiofilters.Distortion` effect."""

    CLIP: DistortionMode
    """Digital distortion effect which cuts off peaks at the top and bottom of the waveform."""

    LOFI: DistortionMode
    """Low-resolution digital distortion effect (bit depth reduction). You can use it to emulate the sound of early digital audio devices."""

    OVERDRIVE: DistortionMode
    """Emulates the warm distortion produced by a field effect transistor, which is commonly used in solid-state musical instrument amplifiers. The `audiofilters.Distortion.drive` property has no effect in this mode."""

    WAVESHAPE: DistortionMode
    """Waveshaper distortions are used mainly by electronic musicians to achieve an extra-abrasive sound."""

class Distortion:
    """A Distortion effect"""

    def __init__(
        self,
        drive: synthio.BlockInput = 0.0,
        pre_gain: synthio.BlockInput = 0.0,
        post_gain: synthio.BlockInput = 0.0,
        mode: DistortionMode = DistortionMode.CLIP,
        soft_clip: bool = False,
        mix: synthio.BlockInput = 1.0,
        buffer_size: int = 512,
        sample_rate: int = 8000,
        bits_per_sample: int = 16,
        samples_signed: bool = True,
        channel_count: int = 1,
    ) -> None:
        """Create a Distortion effect where the original sample is manipulated to create a distorted
           sound according to the DistortionMode.

           The mix parameter allows you to change how much of the unchanged sample passes through to
           the output to how much of the effect audio you hear as the output.

        :param synthio.BlockInput drive: Distortion power. Value can range from 0.0 to 1.0.
        :param synthio.BlockInput pre_gain: Increases or decreases the volume before the effect, in decibels. Value can range from -60 to 60.
        :param synthio.BlockInput post_gain: Increases or decreases the volume after the effect, in decibels. Value can range from -80 to 24.
        :param DistortionMode mode: Distortion type.
        :param bool soft_clip: Whether or not to soft clip (True) or hard clip (False) the output.
        :param synthio.BlockInput mix: The mix as a ratio of the sample (0.0) to the effect (1.0).
        :param int buffer_size: The total size in bytes of each of the two playback buffers to use
        :param int sample_rate: The sample rate to be used
        :param int channel_count: The number of channels the source samples contain. 1 = mono; 2 = stereo.
        :param int bits_per_sample: The bits per sample of the effect
        :param bool samples_signed: Effect is signed (True) or unsigned (False)

        Playing adding a distortion to a synth::

          import time
          import board
          import audiobusio
          import synthio
          import audiofilters

          audio = audiobusio.I2SOut(bit_clock=board.GP20, word_select=board.GP21, data=board.GP22)
          synth = synthio.Synthesizer(channel_count=1, sample_rate=44100)
          effect = audiofilters.Distortion(drive=0.5, mix=1.0, buffer_size=1024, channel_count=1, sample_rate=44100)
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
        """Deinitialises the Distortion."""
        ...

    def __enter__(self) -> Distortion:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    drive: synthio.BlockInput
    """Distortion power. Value can range from 0.0 to 1.0."""
    pre_gain: synthio.BlockInput
    """Increases or decreases the volume before the effect, in decibels. Value can range from -60 to 60."""
    post_gain: synthio.BlockInput
    """Increases or decreases the volume after the effect, in decibels. Value can range from -80 to 24."""
    mode: DistortionMode
    """Distortion type."""
    soft_clip: bool
    """Whether or not to soft clip (True) or hard clip (False) the output."""
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

class Filter:
    """A Filter effect"""

    def __init__(
        self,
        filter: Optional[synthio.AnyBiquad | Tuple[synthio.AnyBiquad]] = None,
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

        :param Optional[synthio.AnyBiquad|Tuple[synthio.AnyBiquad]] filter: A normalized biquad filter object or tuple of normalized biquad filter objects. The sample is processed sequentially by each filter to produce the output samples.
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
    filter: synthio.AnyBiquad | Tuple[synthio.AnyBiquad] | None
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
