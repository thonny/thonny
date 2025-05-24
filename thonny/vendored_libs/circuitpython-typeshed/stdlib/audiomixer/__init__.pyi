"""Support for audio mixing"""

from __future__ import annotations

from typing import Tuple

import circuitpython_typing
import synthio

class Mixer:
    """Mixes one or more audio samples together into one sample."""

    def __init__(
        self,
        voice_count: int = 2,
        buffer_size: int = 1024,
        channel_count: int = 2,
        bits_per_sample: int = 16,
        samples_signed: bool = True,
        sample_rate: int = 8000,
    ) -> None:
        """Create a Mixer object that can mix multiple channels with the same sample rate.
        Samples are accessed and controlled with the mixer's `audiomixer.MixerVoice` objects.

        :param int voice_count: The maximum number of voices to mix
        :param int buffer_size: The total size in bytes of the buffers to mix into
        :param int channel_count: The number of channels the source samples contain. 1 = mono; 2 = stereo.
        :param int bits_per_sample: The bits per sample of the samples being played
        :param bool samples_signed: Samples are signed (True) or unsigned (False)
        :param int sample_rate: The sample rate to be used for all samples

        Playing a wave file from flash::

          import board
          import audioio
          import audiocore
          import audiomixer
          import digitalio

          a = audioio.AudioOut(board.A0)
          music = audiocore.WaveFile(open("cplay-5.1-16bit-16khz.wav", "rb"))
          drum = audiocore.WaveFile(open("drum.wav", "rb"))
          mixer = audiomixer.Mixer(voice_count=2, sample_rate=16000, channel_count=1,
                                   bits_per_sample=16, samples_signed=True)

          print("playing")
          # Have AudioOut play our Mixer source
          a.play(mixer)
          # Play the first sample voice
          mixer.voice[0].play(music)
          while mixer.playing:
            # Play the second sample voice
            mixer.voice[1].play(drum)
            time.sleep(1)
          print("stopped")"""
        ...

    def deinit(self) -> None:
        """Deinitialises the Mixer and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> Mixer:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    playing: bool
    """True when any voice is being output. (read-only)"""
    sample_rate: int
    """32 bit value that dictates how quickly samples are played in Hertz (cycles per second)."""
    voice: Tuple[MixerVoice, ...]
    """A tuple of the mixer's `audiomixer.MixerVoice` object(s).

    .. code-block:: python

       >>> mixer.voice
       (<MixerVoice>,)"""

    def play(
        self,
        sample: circuitpython_typing.AudioSample,
        *,
        voice: int = 0,
        loop: bool = False,
    ) -> None:
        """Plays the sample once when loop=False and continuously when loop=True.
        Does not block. Use `playing` to block.

        Sample must be an `audiocore.WaveFile`, `audiocore.RawSample`, `audiomixer.Mixer` or `audiomp3.MP3Decoder`.

        The sample must match the Mixer's encoding settings given in the constructor."""
        ...

    def stop_voice(self, voice: int = 0) -> None:
        """Stops playback of the sample on the given voice."""
        ...

class MixerVoice:
    """Voice objects used with Mixer

    Used to access and control samples with `audiomixer.Mixer`."""

    def __init__(self) -> None:
        """MixerVoice instance object(s) created by `audiomixer.Mixer`."""
        ...

    def play(
        self, sample: circuitpython_typing.AudioSample, *, loop: bool = False
    ) -> None:
        """Plays the sample once when ``loop=False``, and continuously when ``loop=True``.
        Does not block. Use `playing` to block.

        Sample must be an `audiocore.WaveFile`, `audiocore.RawSample`, `audiomixer.Mixer` or `audiomp3.MP3Decoder`.

        The sample must match the `audiomixer.Mixer`'s encoding settings given in the constructor.
        """
        ...

    def stop(self) -> None:
        """Stops playback of the sample on this voice."""
        ...
    level: synthio.BlockInput
    """The volume level of a voice, as a floating point number between 0 and 1. If your board
    does not support synthio, this property will only accept a float value.
    """
    loop: bool
    """Get or set the loop status of the currently playing sample."""
    playing: bool
    """True when this voice is being output. (read-only)"""
