"""Support for multi-channel audio synthesis

At least 2 simultaneous notes are supported.  samd5x, mimxrt10xx and rp2040 platforms support up to 12 notes.
"""

from __future__ import annotations

import typing
from typing import List, Optional, Sequence, Tuple, Union

from circuitpython_typing import ReadableBuffer

AnyBiquad = Union["Biquad", "BlockBiquad"]

class EnvelopeState:
    ATTACK: EnvelopeState
    """The note is in its attack phase"""
    DECAY: EnvelopeState
    """The note is in its decay phase"""
    SUSTAIN: EnvelopeState
    """The note is in its sustain phase"""
    RELEASE: EnvelopeState
    """The note is in its release phase"""

BlockInput = Union["Math", "LFO", float, None]
"""Blocks and Notes can take any of these types as inputs on certain attributes

A BlockInput can be any of the following types: `Math`, `LFO`, `builtins.float`, `None` (treated same as 0).
"""

class Envelope:
    def __init__(
        self,
        *,
        attack_time: Optional[float] = 0.1,
        decay_time: Optional[float] = 0.05,
        release_time: Optional[float] = 0.2,
        attack_level: Optional[float] = 1.0,
        sustain_level: Optional[float] = 0.8,
    ) -> None:
        """Construct an Envelope object

        The Envelope defines an ADSR (Attack, Decay, Sustain, Release) envelope with linear amplitude ramping. A note starts at 0 volume, then increases to ``attack_level`` over ``attack_time`` seconds; then it decays to ``sustain_level`` over ``decay_time`` seconds. Finally, when the note is released, it decreases to ``0`` volume over ``release_time``.

        If the ``sustain_level`` of an envelope is 0, then the decay and sustain phases of the note are always omitted. The note is considered to be released as soon as the envelope reaches the end of the attack phase. The ``decay_time`` is ignored. This is similar to how a plucked or struck instrument behaves.

        If a note is released before it reaches its sustain phase, it decays with the same slope indicated by ``sustain_level/release_time`` (or ``attack_level/release_time`` for plucked envelopes)

        :param float attack_time: The time in seconds it takes to ramp from 0 volume to attack_volume
        :param float decay_time: The time in seconds it takes to ramp from attack_volume to sustain_volume
        :param float release_time: The time in seconds it takes to ramp from sustain_volume to release_volume. When a note is released before it has reached the sustain phase, the release is done with the same slope indicated by ``release_time`` and ``sustain_level``. If the ``sustain_level`` is ``0.0`` then the release slope calculations use the ``attack_level`` instead.
        :param float attack_level: The level, in the range ``0.0`` to ``1.0`` of the peak volume of the attack phase
        :param float sustain_level: The level, in the range ``0.0`` to ``1.0`` of the volume of the sustain phase relative to the attack level
        """
    attack_time: float
    """The time in seconds it takes to ramp from 0 volume to attack_volume"""

    decay_time: float
    """The time in seconds it takes to ramp from attack_volume to sustain_volume"""

    release_time: float
    """The time in seconds it takes to ramp from sustain_volume to release_volume. When a note is released before it has reached the sustain phase, the release is done with the same slope indicated by ``release_time`` and ``sustain_level``"""

    attack_level: float
    """The level, in the range ``0.0`` to ``1.0`` of the peak volume of the attack phase"""

    sustain_level: float
    """The level, in the range ``0.0`` to ``1.0`` of the volume of the sustain phase relative to the attack level"""

def from_file(
    file: typing.BinaryIO,
    *,
    sample_rate: int = 11025,
    waveform: Optional[ReadableBuffer] = None,
    envelope: Optional[Envelope] = None,
) -> MidiTrack:
    """Create an AudioSample from an already opened MIDI file.
    Currently, only single-track MIDI (type 0) is supported.

    :param typing.BinaryIO file: Already opened MIDI file
    :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
    :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
    :param Envelope envelope: An object that defines the loudness of a note over time. The default envelope provides no ramping, voices turn instantly on and off.

    Playing a MIDI file from flash::

          import audioio
          import board
          import synthio

          data = open("single-track.midi", "rb")
          midi = synthio.from_file(data)
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(midi)
          while a.playing:
            pass
          print("stopped")"""
    ...

def midi_to_hz(midi_note: float) -> float:
    """Converts the given midi note (60 = middle C, 69 = concert A) to Hz"""

def voct_to_hz(ctrl: float) -> float:
    """Converts a 1v/octave signal to Hz.

    24/12 (2.0) corresponds to middle C, 33/12 (2.75) is concert A."""

waveform_max_length: int
"""The maximum number of samples permitted in a waveform"""

class Biquad:
    def __init__(self, b0: float, b1: float, b2: float, a1: float, a2: float) -> None:
        """Construct a normalized biquad filter object.

        This implements the "direct form 1" biquad filter, where each coefficient
        has been pre-divided by a0.

        Biquad objects are usually constructed via one of the related methods on a `Synthesizer` object
        rather than directly from coefficients.

        https://github.com/WebAudio/Audio-EQ-Cookbook/blob/main/Audio-EQ-Cookbook.txt

        .. note:: This is deprecated in ``9.x.x`` and will be removed in ``10.0.0``. Use `BlockBiquad` objects instead.
        """

class FilterMode:
    """The type of filter"""

    LOW_PASS: FilterMode
    """A low-pass filter"""
    HIGH_PASS: FilterMode
    """A high-pass filter"""
    BAND_PASS: FilterMode
    """A band-pass filter"""
    NOTCH: FilterMode
    """A notch filter"""
    LOW_SHELF: FilterMode
    """A low shelf filter"""
    HIGH_SHELF: FilterMode
    """A high shelf filter"""
    PEAKING_EQ: FilterMode
    """A peaking equalizer filter"""

class BlockBiquad:
    def __init__(
        self,
        mode: FilterMode,
        frequency: BlockInput,
        Q: BlockInput = 0.7071067811865475,
        A: BlockInput = None,
    ) -> None:
        """Construct a biquad filter object with given settings.

        ``frequency`` gives the center frequency or corner frequency of the filter,
        depending on the mode.

        ``Q`` gives the gain or sharpness of the filter.

        ``A`` controls the gain of peaking and shelving filters according to the
        formula ``A = 10^(dBgain/40)``. For other filter types it is ignored.

        Since ``frequency`` and ``Q`` are `BlockInput` objects, they can
        be varied dynamically. Internally, this is evaluated as "direct form 1"
        biquad filter.

        The internal filter state x[] and y[] is not updated when the filter
        coefficients change, and there is no theoretical justification for why
        this should result in a stable filter output. However, in practice,
        slowly varying the filter's characteristic frequency and sharpness
        appears to work as you'd expect."""
    mode: FilterMode
    """The mode of filter (read-only)"""

    frequency: BlockInput
    """The central frequency (in Hz) of the filter"""

    Q: BlockInput
    """The sharpness (Q) of the filter"""

    A: BlockInput
    """The gain (A) of the filter

    This setting only has an effect for peaking and shelving EQ filters. It is related
    to the filter gain according to the formula ``A = 10^(dBgain/40)``.
    """

class LFO:
    """A low-frequency oscillator block

    Every `rate` seconds, the output of the LFO cycles through its `waveform`.
    The output at any particular moment is ``waveform[idx] * scale + offset``.

    If `waveform` is None, a triangle waveform is used.

    `rate`, `phase_offset`, `offset`, `scale`, and `once` can be changed at
    run-time. `waveform` may be mutated.

    `waveform` must be a ``ReadableBuffer`` with elements of type ``'h'``
    (16-bit signed integer).  Internally, the elements of `waveform` are scaled
    so that the input range ``[-32768,32767]`` maps to ``[-1.0, 0.99996]``.

    An LFO only updates if it is actually associated with a playing `Synthesizer`,
    including indirectly via a `Note` or another intermediate LFO.

    Using the same LFO as an input to multiple other LFOs or Notes is OK, but
    the result if an LFO is tied to multiple `Synthesizer` objects is undefined.

    In the current implementation, LFOs are updated every 256 samples. This
    should be considered an implementation detail, though it affects how LFOs
    behave for instance when used to implement an integrator (``l.offset = l``).

    An LFO's ``value`` property is computed once when it is constructed, and then
    when its associated synthesizer updates it.

    This means that for instance an LFO **created** with ``offset=1`` has ``value==1``
    immediately, but **updating** the ``offset`` property alone does not
    change ``value``; it only updates through an association with an active synthesizer.

    The interpolation of the waveform is necessarily different depending on the
    ``once`` property. Consider a LFO with ``waveform=np.array([0, 100],
    dtype=np.int16), interpolate=True, once=True, rate=1``. Over 1 second this
    LFO's output will change from ``0`` to ``100``, and will remain at
    ``100`` thereafter, creating a "bend out" over a duration of 1 second.

    However, when ``once=False``, this creates a triangle waveform with a
    period of 1 second. Over about the first half second the input will
    increase from ``0`` to ``100``, then during the second half of the second
    it will decrease back to ``0``.

    The time of the peak output is different depending on the value of ``once``:
    At 1.0s for ``once=True`` and at 0.5s for ``once=False``.

    Because of this difference in interpolation, dynamically updating the
    ``once`` flag except when the LFO is at a phase of 0 will cause a step in
    the LFO's output.
    """

    def __init__(
        self,
        waveform: Optional[ReadableBuffer] = None,
        *,
        rate: BlockInput = 1.0,
        scale: BlockInput = 1.0,
        offset: BlockInput = 0.0,
        phase_offset: BlockInput = 0.0,
        once: bool = False,
        interpolate: bool = True,
    ) -> None:
        pass
    waveform: Optional[ReadableBuffer]
    """The waveform of this lfo. (read-only, but the values in the buffer may be modified dynamically)"""
    rate: BlockInput
    """The rate (in Hz) at which the LFO cycles through its waveform"""
    offset: BlockInput
    """An additive value applied to the LFO's output"""
    phase_offset: BlockInput
    """An additive value applied to the LFO's phase"""
    scale: BlockInput
    """An multiplier value applied to the LFO's output"""

    once: bool
    """True if the waveform should stop when it reaches its last output value, false if it should re-start at the beginning of its waveform

    This applies to the ``phase`` *before* the addition of any ``phase_offset`` """

    interpolate: bool
    """True if the waveform should perform linear interpolation between values"""

    phase: float
    """The phase of the oscillator, in the range 0 to 1 (read-only)"""

    value: float
    """The value of the oscillator (read-only)"""

    def retrigger(self) -> None:
        """Reset the LFO's internal index to the start of the waveform. Most useful when it its `once` property is `True`."""

class MathOperation:
    """Operation for a Math block"""

    def __call__(self, a: BlockInput, b: BlockInput = 0.0, c: BlockInput = 1.0) -> Math:
        """A MathOperation enumeration value can be called to construct a Math block that performs that operation"""
    SUM: "MathOperation"
    """Computes ``a+b+c``. For 2-input sum, set one argument to ``0.0``. To hold a control value for multiple subscribers, set two arguments to ``0.0``."""

    ADD_SUB: "MathOperation"
    """Computes ``a+b-c``. For 2-input subtraction, set ``b`` to ``0.0``."""

    PRODUCT: "MathOperation"
    """Computes ``a*b*c``. For 2-input product, set one argument to ``1.0``."""

    MUL_DIV: "MathOperation"
    """Computes ``a*b/c``. If ``c`` is zero, the output is ``1.0``."""

    SCALE_OFFSET: "MathOperation"
    """Computes ``(a*b)+c``."""

    OFFSET_SCALE: "MathOperation"
    """Computes ``(a+b)*c``. For 2-input multiplication, set ``b`` to 0."""

    LERP: "MathOperation"
    """Computes ``a * (1-c) + b * c``."""

    CONSTRAINED_LERP: "MathOperation"
    """Computes ``a * (1-c') + b * c'``, where ``c'`` is constrained to be between ``0.0`` and ``1.0``."""

    DIV_ADD: "MathOperation"
    """Computes ``a/b+c``.  If ``b`` is zero, the output is ``c``."""

    ADD_DIV: "MathOperation"
    """Computes ``(a+b)/c``.  For 2-input product, set ``b`` to ``0.0``."""

    MID: "MathOperation"
    """Returns the middle of the 3 input values."""

    MAX: "MathOperation"
    """Returns the biggest of the 3 input values."""

    MIN: "MathOperation"
    """Returns the smallest of the 3 input values."""

    ABS: "MathOperation"
    """Returns the absolute value of ``a``."""

class Math:
    """An arithmetic block

    Performs an arithmetic operation on up to 3 inputs. See the
    documentation of ``MathOperation`` for the specific functions available.

    The properties can all be changed at run-time.

    An Math only updates if it is actually associated with a playing `Synthesizer`,
    including indirectly via a `Note` or another intermediate Math.

    Using the same Math as an input to multiple other Maths or Notes is OK, but
    the result if an Math is tied to multiple `Synthesizer` objects is undefined.

    In the current implementation, Maths are updated every 256 samples. This
    should be considered an implementation detail.
    """

    def __init__(
        self,
        operation: MathOperation,
        a: BlockInput,
        b: BlockInput = 0.0,
        c: BlockInput = 1.0,
    ) -> None:
        pass
    a: BlockInput
    """The first input to the operation"""
    b: BlockInput
    """The second input to the operation"""
    c: BlockInput
    """The third input to the operation"""
    operation: MathOperation
    """The function to compute"""

    value: float
    """The value of the oscillator (read-only)"""

class MidiTrack:
    """Simple MIDI synth"""

    def __init__(
        self,
        buffer: ReadableBuffer,
        tempo: int,
        *,
        sample_rate: int = 11025,
        waveform: Optional[ReadableBuffer] = None,
        envelope: Optional[Envelope] = None,
    ) -> None:
        """Create a MidiTrack from the given stream of MIDI events. Only "Note On" and "Note Off" events
        are supported; channel numbers and key velocities are ignored. Up to two notes may be on at the
        same time.

        :param ~circuitpython_typing.ReadableBuffer buffer: Stream of MIDI events, as stored in a MIDI file track chunk
        :param int tempo: Tempo of the streamed events, in MIDI ticks per second
        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
        :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
        :param Envelope envelope: An object that defines the loudness of a note over time. The default envelope provides no ramping, voices turn instantly on and off.

        Simple melody::

          import audioio
          import board
          import synthio

          dac = audioio.AudioOut(board.SPEAKER)
          melody = synthio.MidiTrack(b"\\0\\x90H\\0*\\x80H\\0\\6\\x90J\\0*\\x80J\\0\\6\\x90L\\0*\\x80L\\0\\6\\x90J\\0" +
                                     b"*\\x80J\\0\\6\\x90H\\0*\\x80H\\0\\6\\x90J\\0*\\x80J\\0\\6\\x90L\\0T\\x80L\\0" +
                                     b"\\x0c\\x90H\\0T\\x80H\\0\\x0c\\x90H\\0T\\x80H\\0", tempo=640)
          dac.play(melody)
          print("playing")
          while dac.playing:
            pass
          print("stopped")"""
        ...

    def deinit(self) -> None:
        """Deinitialises the MidiTrack and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> MidiTrack:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    sample_rate: int
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""

    error_location: Optional[int]
    """Offset, in bytes within the midi data, of a decoding error"""

class Note:
    def __init__(
        self,
        *,
        frequency: float,
        panning: BlockInput = 0.0,
        waveform: Optional[ReadableBuffer] = None,
        waveform_loop_start: BlockInput = 0,
        waveform_loop_end: BlockInput = waveform_max_length,
        envelope: Optional[Envelope] = None,
        amplitude: BlockInput = 1.0,
        bend: BlockInput = 0.0,
        filter: Optional[AnyBiquad] = None,
        ring_frequency: float = 0.0,
        ring_bend: float = 0.0,
        ring_waveform: Optional[ReadableBuffer] = None,
        ring_waveform_loop_start: BlockInput = 0,
        ring_waveform_loop_end: BlockInput = waveform_max_length,
    ) -> None:
        """Construct a Note object, with a frequency in Hz, and optional panning, waveform, envelope, tremolo (volume change) and bend (frequency change).

        If waveform or envelope are `None` the synthesizer object's default waveform or envelope are used.

        If the same Note object is played on multiple Synthesizer objects, the result is undefined.
        """
    frequency: float
    """The base frequency of the note, in Hz."""
    filter: Optional[AnyBiquad]
    """If not None, the output of this Note is filtered according to the provided coefficients.

    Construct an appropriate filter by calling a filter-making method on the
    `Synthesizer` object where you plan to play the note, as filter coefficients depend
    on the sample rate"""
    panning: BlockInput
    """Defines the channel(s) in which the note appears.

    -1 is left channel only, 0 is both channels, and 1 is right channel.
    For fractional values, the note plays at full amplitude in one channel
    and partial amplitude in the other channel. For instance -.5 plays at full
    amplitude in the left channel and 1/2 amplitude in the right channel."""
    amplitude: BlockInput
    """The relative amplitude of the note, from 0 to 1

    An amplitude of 0 makes the note inaudible. It is combined multiplicatively with
    the value from the note's envelope.

    To achieve a tremolo effect, attach an LFO here."""

    bend: BlockInput
    """The pitch bend depth of the note, from -12 to +12

    A depth of 0 plays the programmed frequency. A depth of 1 corresponds to a bend of 1
    octave.  A depth of (1/12) = 0.0833 corresponds to a bend of 1 semitone,
    and a depth of .00833 corresponds to one musical cent.

    To achieve a vibrato or sweep effect, attach an LFO here.
    """
    waveform: Optional[ReadableBuffer]
    """The waveform of this note. Setting the waveform to a buffer of a different size resets the note's phase."""
    waveform_loop_start: BlockInput
    """The sample index of where to begin looping waveform data.

    The value is limited to the range ``0`` to ``len(waveform)-1`` (inclusive)."""
    waveform_loop_end: BlockInput
    """The sample index of where to end looping waveform data.

    The value is limited to the range ``waveform_loop_start+1`` to ``len(waveform)`` (inclusive).

    Use the `synthio.waveform_max_length` constant to set the loop point at the end of the wave form, no matter its length."""

    envelope: Envelope
    """The envelope of this note"""

    ring_frequency: float
    """The ring frequency of the note, in Hz. Zero disables.

    For ring to take effect, both ``ring_frequency`` and ``ring_waveform`` must be set."""
    ring_bend: float
    """The pitch bend depth of the note's ring waveform, from -12 to +12

    A depth of 0 plays the programmed frequency. A depth of 1 corresponds to a bend of 1
    octave.  A depth of (1/12) = 0.0833 corresponds to a bend of 1 semitone,
    and a depth of .00833 corresponds to one musical cent.

    To achieve a vibrato or sweep effect on the ring waveform, attach an LFO here.
    """
    ring_waveform: Optional[ReadableBuffer]
    """The ring waveform of this note. Setting the ring_waveform to a buffer of a different size resets the note's phase.

    For ring to take effect, both ``ring_frequency`` and ``ring_waveform`` must be set."""

    ring_waveform_loop_start: BlockInput
    """The sample index of where to begin looping waveform data.

    The value is limited to the range ``0`` to ``len(ring_waveform)-1`` (inclusive)."""
    ring_waveform_loop_end: BlockInput
    """The sample index of where to end looping waveform data.

    The value is limited to the range ``ring_waveform_loop_start+1`` to ``len(ring_waveform)`` (inclusive).

    Use the `synthio.waveform_max_length` constant to set the loop point at the end of the wave form, no matter its length."""

NoteSequence = Sequence[Union[int, Note]]
"""A sequence of notes, which can each be integer MIDI note numbers or `Note` objects"""
NoteOrNoteSequence = Union[int, Note, NoteSequence]
"""A note or sequence of notes"""
LFOOrLFOSequence = Union["LFO", Sequence["LFO"]]
"""An LFO or a sequence of LFOs"""

class Synthesizer:
    def __init__(
        self,
        *,
        sample_rate: int = 11025,
        channel_count: int = 1,
        waveform: Optional[ReadableBuffer] = None,
        envelope: Optional[Envelope] = None,
    ) -> None:
        """Create a synthesizer object.

        This API is experimental.

        Integer notes use MIDI note numbering, with 60 being C4 or Middle C,
        approximately 262Hz. Integer notes use the given waveform & envelope,
        and do not support advanced features like tremolo or vibrato.

        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
        :param int channel_count: The number of output channels (1=mono, 2=stereo)
        :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
        :param Optional[Envelope] envelope: An object that defines the loudness of a note over time. The default envelope, `None` provides no ramping, voices turn instantly on and off.
        """

    def press(self, /, press: NoteOrNoteSequence = ()) -> None:
        """Turn some notes on.

        Pressing a note that was already pressed has no effect.

        :param NoteOrNoteSequence press: Any sequence of notes."""

    def release(self, /, release: NoteOrNoteSequence = ()) -> None:
        """Turn some notes off.

        Releasing a note that was already released has no effect.

        :param NoteOrNoteSequence release: Any sequence of notes."""

    def change(
        self,
        release: NoteOrNoteSequence = (),
        press: NoteOrNoteSequence = (),
        retrigger: LFOOrLFOSequence = (),
    ) -> None:
        """Start notes, stop them, and/or re-trigger some LFOs.

        The changes all happen atomically with respect to output generation.

        It is OK to release note that was not actually turned on.

        Pressing a note that was already pressed returns it to the attack phase
        but without resetting its amplitude. Releasing a note and immediately
        pressing it again returns it to the attack phase with an initial
        amplitude of 0.

        At the same time, the passed LFOs (if any) are retriggered.

        :param NoteOrNoteSequence release: Any sequence of notes.
        :param NoteOrNoteSequence press: Any sequence of notes.
        :param LFOOrLFOSequence retrigger: Any sequence of LFOs.

        Note: for compatibility, ``release_then_press`` may be used as an alias
        for this function. This compatibility name will be removed in 9.0."""

    def release_all_then_press(self, /, press: NoteOrNoteSequence) -> None:
        """Turn any currently-playing notes off, then turn on the given notes

        Releasing a note and immediately pressing it again returns it to the
        attack phase with an initial amplitude of 0.

        :param NoteOrNoteSequence press: Any sequence of notes."""

    def release_all(self) -> None:
        """Turn any currently-playing notes off"""

    def deinit(self) -> None:
        """Deinitialises the object and releases any memory resources for reuse."""
        ...

    def __enter__(self) -> Synthesizer:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    envelope: Optional[Envelope]
    """The envelope to apply to all notes. `None`, the default envelope, instantly turns notes on and off. The envelope may be changed dynamically, but it affects all notes (even currently playing notes)"""
    sample_rate: int
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""
    pressed: NoteSequence
    """A sequence of the currently pressed notes (read-only property).

    This does not include notes in the release phase of the envelope."""

    def note_info(self, note: Note) -> Tuple[Optional[EnvelopeState], float]:
        """Get info about a note's current envelope state

        If the note is currently playing (including in the release phase), the returned value gives the current envelope state and the current envelope value.

        If the note is not playing on this synthesizer, returns the tuple ``(None, 0.0)``.
        """
    blocks: List[BlockInput]
    """A list of blocks to advance whether or not they are associated with a playing note.

    This can be used to implement 'free-running' LFOs. LFOs associated with playing notes are advanced whether or not they are in this list.

    This property is read-only but its contents may be modified by e.g., calling ``synth.blocks.append()`` or ``synth.blocks.remove()``. It is initially an empty list."""

    max_polyphony: int
    """Maximum polyphony of the synthesizer (read-only class property)"""

    def low_pass_filter(cls, frequency: float, Q: float = 0.7071067811865475) -> Biquad:
        """Construct a low-pass filter with the given parameters.

        ``frequency``, called f0 in the cookbook, is the corner frequency in Hz
        of the filter.

        ``Q`` controls how peaked the response will be at the cutoff frequency. A large value makes the response more peaked.

        .. note:: This is deprecated in ``9.x.x`` and will be removed in ``10.0.0``. Use `BlockBiquad` objects instead.
        """

    def high_pass_filter(
        cls, frequency: float, Q: float = 0.7071067811865475
    ) -> Biquad:
        """Construct a high-pass filter with the given parameters.

        ``frequency``, called f0 in the cookbook, is the corner frequency in Hz
        of the filter.

        ``Q`` controls how peaked the response will be at the cutoff frequency. A large value makes the response more peaked.

        .. note:: This is deprecated in ``9.x.x`` and will be removed in ``10.0.0``. Use `BlockBiquad` objects instead.
        """

    def band_pass_filter(
        cls, frequency: float, Q: float = 0.7071067811865475
    ) -> Biquad:
        """Construct a band-pass filter with the given parameters.

        ``frequency``, called f0 in the cookbook, is the center frequency in Hz
        of the filter.

        ``Q`` Controls how peaked the response will be at the cutoff frequency. A large value makes the response more peaked.

        The coefficients are scaled such that the filter has a 0dB peak gain.

        .. note:: This is deprecated in ``9.x.x`` and will be removed in ``10.0.0``. Use `BlockBiquad` objects instead.
        """
