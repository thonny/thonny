"""Support for audio delay effects

The `audiodelays` module contains classes to provide access to audio delay effects.

"""

from __future__ import annotations

import circuitpython_typing
import synthio

class Echo:
    """An Echo effect"""

    def __init__(
        self,
        max_delay_ms: int = 500,
        delay_ms: synthio.BlockInput = 250.0,
        decay: synthio.BlockInput = 0.7,
        mix: synthio.BlockInput = 0.5,
        buffer_size: int = 512,
        sample_rate: int = 8000,
        bits_per_sample: int = 16,
        samples_signed: bool = True,
        channel_count: int = 1,
    ) -> None:
        """Create a Echo effect where you hear the original sample play back, at a lesser volume after
           a set number of millisecond delay. The delay timing of the echo can be changed at runtime
           with the delay_ms parameter but the delay can never exceed the max_delay_ms parameter. The
           maximum delay you can set is limited by available memory.

           Each time the echo plays back the volume is reduced by the decay setting (echo * decay).

           The mix parameter allows you to change how much of the unchanged sample passes through to
           the output to how much of the effect audio you hear as the output.

        :param int max_delay_ms: The maximum time the echo can be in milliseconds
        :param synthio.BlockInput delay_ms: The current time of the echo delay in milliseconds. Must be less the max_delay_ms
        :param synthio.BlockInput decay: The rate the echo fades. 0.0 = instant; 1.0 = never.
        :param synthio.BlockInput mix: The mix as a ratio of the sample (0.0) to the effect (1.0).
        :param int buffer_size: The total size in bytes of each of the two playback buffers to use
        :param int sample_rate: The sample rate to be used
        :param int channel_count: The number of channels the source samples contain. 1 = mono; 2 = stereo.
        :param int bits_per_sample: The bits per sample of the effect
        :param bool samples_signed: Effect is signed (True) or unsigned (False)
        :param bool freq_shift: Do echos change frequency as the echo delay changes

        Playing adding an echo to a synth::

          import time
          import board
          import audiobusio
          import synthio
          import audiodelays

          audio = audiobusio.I2SOut(bit_clock=board.GP20, word_select=board.GP21, data=board.GP22)
          synth = synthio.Synthesizer(channel_count=1, sample_rate=44100)
          echo = audiodelays.Echo(max_delay_ms=1000, delay_ms=850, decay=0.65, buffer_size=1024, channel_count=1, sample_rate=44100, mix=0.7, freq_shift=False)
          echo.play(synth)
          audio.play(echo)

          note = synthio.Note(261)
          while True:
              synth.press(note)
              time.sleep(0.25)
              synth.release(note)
              time.sleep(5)"""
        ...

    def deinit(self) -> None:
        """Deinitialises the Echo."""
        ...

    def __enter__(self) -> Echo:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    delay_ms: synthio.BlockInput
    """Delay of the echo in milliseconds. (read-only)"""

    decay: synthio.BlockInput
    """The rate the echo decays between 0 and 1 where 1 is forever and 0 is no echo."""
    mix: synthio.BlockInput
    """The rate the echo mix between 0 and 1 where 0 is only sample and 1 is all effect."""
    freq_shift: bool
    """Does the echo change frequencies as the delay changes."""
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
        """Stops playback of the sample. The echo continues playing."""
        ...

class PitchShift:
    """A pitch shift effect"""

    def __init__(
        self,
        semitones: synthio.BlockInput = 0.0,
        mix: synthio.BlockInput = 1.0,
        window: int = 1024,
        overlap: int = 128,
        buffer_size: int = 512,
        sample_rate: int = 8000,
        bits_per_sample: int = 16,
        samples_signed: bool = True,
        channel_count: int = 1,
    ) -> None:
        """Create a pitch shift effect where the original sample play back is altered to change the
           the perceived pitch by a factor of semi-tones (1/12th of an octave). This effect will cause
           a slight delay in the output depending on the size of the window and overlap buffers.

           The mix parameter allows you to change how much of the unchanged sample passes through to
           the output to how much of the effect audio you hear as the output.

        :param synthio.BlockInput semitones: The amount of pitch shifting in semitones (1/12th of an octave)
        :param synthio.BlockInput mix: The mix as a ratio of the sample (0.0) to the effect (1.0)
        :param int window: The total size in bytes of the window buffer used alter the playback pitch
        :param int overlap: The total size in bytes of the overlap buffer used to prevent popping in the output. If set as 0, no overlap will be used.
        :param int buffer_size: The total size in bytes of each of the two playback buffers to use
        :param int sample_rate: The sample rate to be used
        :param int channel_count: The number of channels the source samples contain. 1 = mono; 2 = stereo.
        :param int bits_per_sample: The bits per sample of the effect
        :param bool samples_signed: Effect is signed (True) or unsigned (False)

        Shifting the pitch of a synth by 5 semitones::

          import time
          import board
          import audiobusio
          import synthio
          import audiodelays

          audio = audiobusio.I2SOut(bit_clock=board.GP0, word_select=board.GP1, data=board.GP2)
          synth = synthio.Synthesizer(channel_count=1, sample_rate=44100)
          pitch_shift = audiodelays.PitchShift(semitones=5.0, mix=0.5, window=2048, overlap=256, buffer_size=1024, channel_count=1, sample_rate=44100)
          pitch_shift.play(synth)
          audio.play(pitch_shift)

          while True:
              for notenum in (60, 64, 67, 71):
                  synth.press(notenum)
                  time.sleep(0.25)
                  synth.release_all()"""
        ...

    def deinit(self) -> None:
        """Deinitialises the PitchShift."""
        ...

    def __enter__(self) -> PitchShift:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    semitones: synthio.BlockInput
    """The amount of pitch shifting in semitones (1/12th of an octave)."""

    mix: synthio.BlockInput
    """The output mix between 0 and 1 where 0 is only sample and 1 is all effect."""
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
