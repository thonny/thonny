"""Audio output via digital PWM

The `audiopwmio` module contains classes to provide access to audio IO.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

Since CircuitPython 5, `Mixer`, `RawSample` and `WaveFile` are moved
to :mod:`audiocore`."""

from __future__ import annotations

from typing import Optional

import circuitpython_typing
import microcontroller

class PWMAudioOut:
    """Output an analog audio signal by varying the PWM duty cycle."""

    def __init__(
        self,
        left_channel: microcontroller.Pin,
        *,
        right_channel: Optional[microcontroller.Pin] = None,
        quiescent_value: int = 0x8000,
    ) -> None:
        """Create a PWMAudioOut object associated with the given pin(s). This allows you to
        play audio signals out on the given pin(s).  In contrast to mod:`audioio`,
        the pin(s) specified are digital pins, and are driven with a device-dependent PWM
        signal.

        :param ~microcontroller.Pin left_channel: The pin to output the left channel to
        :param ~microcontroller.Pin right_channel: The pin to output the right channel to
        :param int quiescent_value: The output value when no signal is present. Samples should start
            and end with this value to prevent audible popping.

        **Limitations:** On mimxrt10xx, low sample rates may have an audible
        "carrier" frequency. The manufacturer datasheet states that the "MQS" peripheral
        is intended for 44 kHz or 48kHz input signals.

        Simple 8ksps 440 Hz sin wave::

          import audiocore
          import audiopwmio
          import board
          import array
          import time
          import math

          # Generate one period of sine wav.
          length = 8000 // 440
          sine_wave = array.array("H", [0] * length)
          for i in range(length):
              sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15)

          dac = audiopwmio.PWMAudioOut(board.SPEAKER)
          sine_wave = audiocore.RawSample(sine_wave, sample_rate=8000)
          dac.play(sine_wave, loop=True)
          time.sleep(1)
          dac.stop()

        Playing a wave file from flash::

          import board
          import audiocore
          import audiopwmio
          import digitalio

          # Required for CircuitPlayground Express
          speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
          speaker_enable.switch_to_output(value=True)

          data = open("cplay-5.1-16bit-16khz.wav", "rb")
          wav = audiocore.WaveFile(data)
          a = audiopwmio.PWMAudioOut(board.SPEAKER)

          print("playing")
          a.play(wav)
          while a.playing:
            pass
          print("stopped")"""
        ...

    def deinit(self) -> None:
        """Deinitialises the PWMAudioOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> PWMAudioOut:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def play(
        self, sample: circuitpython_typing.AudioSample, *, loop: bool = False
    ) -> None:
        """Plays the sample once when loop=False and continuously when loop=True.
        Does not block. Use `playing` to block.

        Sample must be an `audiocore.WaveFile`, `audiocore.RawSample`, `audiomixer.Mixer` or `audiomp3.MP3Decoder`.

        The sample itself should consist of 16 bit samples. Microcontrollers with a lower output
        resolution will use the highest order bits to output."""
        ...

    def stop(self) -> None:
        """Stops playback and resets to the start of the sample."""
        ...
    playing: bool
    """True when an audio sample is being output even if `paused`. (read-only)"""

    def pause(self) -> None:
        """Stops playback temporarily while remembering the position. Use `resume` to resume playback."""
        ...

    def resume(self) -> None:
        """Resumes sample playback after :py:func:`pause`."""
        ...
    paused: bool
    """True when playback is paused. (read-only)"""
