"""Support for audio mixing"""

class Mixer:
    """Mixes one or more audio samples together into one sample."""

    def __init__(self, voice_count: int = 2, buffer_size: int = 1024, channel_count: int = 2, bits_per_sample: int = 16, samples_signed: bool = True, sample_rate: int = 8000):
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

    def deinit(self, ) -> Any:
        """Deinitialises the Mixer and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    playing: Any = ...
    """True when any voice is being output. (read-only)"""

    sample_rate: Any = ...
    """32 bit value that dictates how quickly samples are played in Hertz (cycles per second)."""

    voice: Any = ...
    """A tuple of the mixer's `audiomixer.MixerVoice` object(s).

    .. code-block:: python

       >>> mixer.voice
       (<MixerVoice>,)"""
    def play(self, sample: Any, *, voice: Any = 0, loop: Any = False) -> Any:
        """Plays the sample once when loop=False and continuously when loop=True.
        Does not block. Use `playing` to block.

        Sample must be an `audiocore.WaveFile`, `audiocore.RawSample`, or `audiomixer.Mixer`.

        The sample must match the Mixer's encoding settings given in the constructor."""
        ...

    def stop_voice(self, voice: Any = 0) -> Any:
        """Stops playback of the sample on the given voice."""
        ...

class MixerVoice:
    """Voice objects used with Mixer

    Used to access and control samples with `audiomixer.Mixer`."""

    def __init__(self, ):
        """MixerVoice instance object(s) created by `audiomixer.Mixer`."""
        ...

    def play(self, sample: Any, *, loop: Any = False) -> Any:
        """Plays the sample once when ``loop=False``, and continuously when ``loop=True``.
        Does not block. Use `playing` to block.

        Sample must be an `audiocore.WaveFile`, `audiomixer.Mixer` or `audiocore.RawSample`.

        The sample must match the `audiomixer.Mixer`'s encoding settings given in the constructor."""
        ...

    def stop(self, ) -> Any:
        """Stops playback of the sample on this voice."""
        ...

    level: Any = ...
    """The volume level of a voice, as a floating point number between 0 and 1."""

    playing: Any = ...
    """True when this voice is being output. (read-only)"""

