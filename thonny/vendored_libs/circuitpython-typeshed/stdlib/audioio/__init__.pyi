"""Support for audio output

The `audioio` module contains classes to provide access to audio IO.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For more information on working with this module, refer to the
`CircuitPython Essentials Learn Guide
<https://learn.adafruit.com/circuitpython-essentials/circuitpython-audio-out>`_.

Since CircuitPython 5, `RawSample` and `WaveFile` are moved
to :mod:`audiocore`, and `Mixer` is moved to :mod:`audiomixer`."""

from __future__ import annotations

from typing import Optional

import circuitpython_typing
import microcontroller

class AudioOut:
    """Output an analog audio signal"""

    def __init__(
        self,
        left_channel: microcontroller.Pin,
        *,
        right_channel: Optional[microcontroller.Pin] = None,
        quiescent_value: int = 0x8000,
    ) -> None:
        """Create a AudioOut object associated with the given pin(s). This allows you to
        play audio signals out on the given pin(s).

        :param ~microcontroller.Pin left_channel: Output left channel data to this pin
        :param ~microcontroller.Pin right_channel: Output right channel data to this pin. May be ``None``.
        :param int quiescent_value: The output value when no signal is present. Samples should start
            and end with this value to prevent audible popping.

        .. note:: On ESP32 and ESP32-S2, the DAC channels are usually designated
          as ``DAC_1`` (right stereo channel) and DAC_2 (left stereo channel).
          These pins are sometimes labelled as ``A0`` and ``A1``, but they may be assigned
          in either order. Check your board's pinout to verify which pin is which channel.

        Simple 8ksps 440 Hz sin wave::

          import audiocore
          import audioio
          import board
          import array
          import time
          import math

          # Generate one period of sine wav.
          length = 8000 // 440
          sine_wave = array.array("H", [0] * length)
          for i in range(length):
              sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15)

          dac = audioio.AudioOut(board.SPEAKER)
          sine_wave = audiocore.RawSample(sine_wave, sample_rate=8000)
          dac.play(sine_wave, loop=True)
          time.sleep(1)
          dac.stop()

        Playing a wave file from flash::

          import board
          import audioio
          import digitalio

          # Required for CircuitPlayground Express
          speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
          speaker_enable.switch_to_output(value=True)

          data = open("cplay-5.1-16bit-16khz.wav", "rb")
          wav = audiocore.WaveFile(data)
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(wav)
          while a.playing:
            pass
          print("stopped")"""
        ...

    def deinit(self) -> None:
        """Deinitialises the AudioOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> AudioOut:
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
        resolution will use the highest order bits to output. For example, the SAMD21 has a 10 bit
        DAC that ignores the lowest 6 bits when playing 16 bit samples."""
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
