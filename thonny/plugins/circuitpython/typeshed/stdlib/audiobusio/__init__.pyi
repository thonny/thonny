"""Support for audio input and output over digital buses

The `audiobusio` module contains classes to provide access to audio IO
over digital buses. These protocols are used to communicate audio to other
chips in the same circuit. It doesn't include audio interconnect protocols
such as S/PDIF.

All classes change hardware state and should be deinitialized when they
are no longer needed. To do so, either call :py:meth:`!deinit` or use a
context manager."""

from __future__ import annotations

from typing import Optional

import circuitpython_typing
import microcontroller
from circuitpython_typing import WriteableBuffer

class I2SOut:
    """Output an I2S audio signal"""

    def __init__(
        self,
        bit_clock: microcontroller.Pin,
        word_select: microcontroller.Pin,
        data: microcontroller.Pin,
        *,
        main_clock: Optional[microcontroller.Pin] = None,
        left_justified: bool = False,
    ) -> None:
        """Create a I2SOut object associated with the given pins.

        :param ~microcontroller.Pin bit_clock: The bit clock (or serial clock) pin
        :param ~microcontroller.Pin word_select: The word select (or left/right clock) pin
        :param ~microcontroller.Pin data: The data pin
        :param ~microcontroller.Pin main_clock: The main clock pin
        :param bool left_justified: True when data bits are aligned with the word select clock. False
          when they are shifted by one to match classic I2S protocol.

        Simple 8ksps 440 Hz sine wave on `Metro M0 Express <https://www.adafruit.com/product/3505>`_
        using `UDA1334 Breakout <https://www.adafruit.com/product/3678>`_::

          import audiobusio
          import audiocore
          import board
          import array
          import time
          import math

          # Generate one period of sine wave.
          length = 8000 // 440
          sine_wave = array.array("H", [0] * length)
          for i in range(length):
              sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15)

          sine_wave = audiocore.RawSample(sine_wave, sample_rate=8000)
          i2s = audiobusio.I2SOut(board.D1, board.D0, board.D9)
          i2s.play(sine_wave, loop=True)
          time.sleep(1)
          i2s.stop()

        Playing a wave file from flash::

          import board
          import audiocore
          import audiobusio
          import digitalio


          f = open("cplay-5.1-16bit-16khz.wav", "rb")
          wav = audiocore.WaveFile(f)

          a = audiobusio.I2SOut(board.D1, board.D0, board.D9)

          print("playing")
          a.play(wav)
          while a.playing:
            pass
          print("stopped")"""
        ...

    def deinit(self) -> None:
        """Deinitialises the I2SOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> I2SOut:
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

        The sample itself should consist of 8 bit or 16 bit samples."""
        ...

    def stop(self) -> None:
        """Stops playback."""
        ...
    playing: bool
    """True when the audio sample is being output. (read-only)"""
    def pause(self) -> None:
        """Stops playback temporarily while remembering the position. Use `resume` to resume playback."""
        ...

    def resume(self) -> None:
        """Resumes sample playback after :py:func:`pause`."""
        ...
    paused: bool
    """True when playback is paused. (read-only)"""

class PDMIn:
    """Record an input PDM audio stream"""

    def __init__(
        self,
        clock_pin: microcontroller.Pin,
        data_pin: microcontroller.Pin,
        *,
        sample_rate: int = 16000,
        bit_depth: int = 8,
        mono: bool = True,
        oversample: int = 64,
        startup_delay: float = 0.11,
    ) -> None:
        """Create a PDMIn object associated with the given pins. This allows you to
        record audio signals from the given pins. Individual ports may put further
        restrictions on the recording parameters. The overall sample rate is
        determined by `sample_rate` x ``oversample``, and the total must be 1MHz or
        higher, so `sample_rate` must be a minimum of 16000.

        :param ~microcontroller.Pin clock_pin: The pin to output the clock to
        :param ~microcontroller.Pin data_pin: The pin to read the data from
        :param int sample_rate: Target sample_rate of the resulting samples. Check `sample_rate` for actual value.
          Minimum sample_rate is about 16000 Hz.
        :param int bit_depth: Final number of bits per sample. Must be divisible by 8
        :param bool mono: True when capturing a single channel of audio, captures two channels otherwise
        :param int oversample: Number of single bit samples to decimate into a final sample. Must be divisible by 8
        :param float startup_delay: seconds to wait after starting microphone clock
         to allow microphone to turn on. Most require only 0.01s; some require 0.1s. Longer is safer.
         Must be in range 0.0-1.0 seconds.

        **Limitations:** On SAMD and RP2040, supports only 8 or 16 bit mono input, with 64x oversampling.
        On nRF52840, supports only 16 bit mono input at 16 kHz; oversampling is fixed at 64x. Not provided
        on nRF52833 for space reasons. Not available on Espressif.

        For example, to record 8-bit unsigned samples to a buffer::

          import audiobusio
          import board

          # Prep a buffer to record into
          b = bytearray(200)
          with audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, sample_rate=16000) as mic:
              mic.record(b, len(b))

        To record 16-bit unsigned samples to a buffer::

          import audiobusio
          import board

          # Prep a buffer to record into.
          b = array.array("H", [0] * 200)
          with audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, sample_rate=16000, bit_depth=16) as mic:
              mic.record(b, len(b))
        """
    ...
    def deinit(self) -> None:
        """Deinitialises the PDMIn and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> PDMIn:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context."""
        ...

    def record(self, destination: WriteableBuffer, destination_length: int) -> None:
        """Records destination_length bytes of samples to destination. This is
        blocking.

        An IOError may be raised when the destination is too slow to record the
        audio at the given rate. For internal flash, writing all 1s to the file
        before recording is recommended to speed up writes.

        :return: The number of samples recorded. If this is less than ``destination_length``,
          some samples were missed due to processing time."""
        ...
    sample_rate: int
    """The actual sample_rate of the recording. This may not match the constructed
    sample rate due to internal clock limitations."""
