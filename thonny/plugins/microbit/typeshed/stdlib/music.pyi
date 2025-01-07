"""Create and play melodies.
"""
from typing import Optional, Tuple, Union, List

from .microbit import MicroBitDigitalPin, pin0

DADADADUM: Tuple[str, ...]
"""Melody: the opening to Beethoven’s 5th Symphony in C minor."""

ENTERTAINER: Tuple[str, ...]
"""Melody: the opening fragment of Scott Joplin’s Ragtime classic “The Entertainer”."""

PRELUDE: Tuple[str, ...]
"""Melody: the opening of the first Prelude in C Major of J.S.Bach’s 48 Preludes and Fugues."""

ODE: Tuple[str, ...]
"""Melody: the “Ode to Joy” theme from Beethoven’s 9th Symphony in D minor."""

NYAN: Tuple[str, ...]
"""Melody: the Nyan Cat theme (http://www.nyan.cat/).

The composer is unknown. This is fair use for educational porpoises (as they say in New York)."""

RINGTONE: Tuple[str, ...]
"""Melody: something that sounds like a mobile phone ringtone.

To be used to indicate an incoming message.
"""

FUNK: Tuple[str, ...]
"""Melody: a funky bass line for secret agents and criminal masterminds."""

BLUES: Tuple[str, ...]
"""Melody: a boogie-woogie 12-bar blues walking bass."""

BIRTHDAY: Tuple[str, ...]
"""Melody: “Happy Birthday to You…”

For copyright status see: http://www.bbc.co.uk/news/world-us-canada-34332853
"""

WEDDING: Tuple[str, ...]
"""Melody: the bridal chorus from Wagner’s opera “Lohengrin”."""

FUNERAL: Tuple[str, ...]
"""Melody: the “funeral march” otherwise known as Frédéric Chopin’s Piano Sonata No. 2 in B♭ minor, Op. 35."""

PUNCHLINE: Tuple[str, ...]
"""Melody: a fun fragment that signifies a joke has been made."""

PYTHON: Tuple[str, ...]
"""Melody: John Philip Sousa’s march “Liberty Bell” aka, the theme for “Monty Python’s Flying Circus” (after which the Python programming language is named)."""

BADDY: Tuple[str, ...]
"""Melody: silent movie era entrance of a baddy."""

CHASE: Tuple[str, ...]
"""Melody: silent movie era chase scene."""

BA_DING: Tuple[str, ...]
"""Melody: a short signal to indicate something has happened."""

WAWAWAWAA: Tuple[str, ...]
"""Melody: a very sad trombone."""

JUMP_UP: Tuple[str, ...]
"""Melody: for use in a game, indicating upward movement."""

JUMP_DOWN: Tuple[str, ...]
"""Melody: for use in a game, indicating downward movement."""

POWER_UP: Tuple[str, ...]
"""Melody: a fanfare to indicate an achievement unlocked."""

POWER_DOWN: Tuple[str, ...]
"""Melody: a sad fanfare to indicate an achievement lost."""

def set_tempo(ticks: int = 4, bpm: int = 120) -> None:
    """Sets the approximate tempo for playback.

    Example: ``music.set_tempo(bpm=120)``

    :param ticks: The number of ticks constituting a beat.
    :param bpm: An integer determining how many beats per minute.

    Suggested default values allow the following useful behaviour:

    - music.set_tempo() – reset the tempo to default of ticks = 4, bpm = 120
    - music.set_tempo(ticks=8) – change the “definition” of a beat
    - music.set_tempo(bpm=180) – just change the tempo

    To work out the length of a tick in milliseconds is very simple arithmetic:
    60000/bpm/ticks_per_beat. For the default values that’s
    60000/120/4 = 125 milliseconds or 1 beat = 500 milliseconds.
    """
    ...

def get_tempo() -> Tuple[int, int]:
    """Gets the current tempo as a tuple of integers: ``(ticks, bpm)``.

    Example: ``ticks, beats = music.get_tempo()``

    :return: The temp as a tuple with two integer values, the ticks then the beats per minute.
    """
    ...

def play(
    music: Union[str, List[str], Tuple[str, ...]],
    pin: Optional[MicroBitDigitalPin] = pin0,
    wait: bool = True,
    loop: bool = False,
) -> None:
    """Plays music.

    Example: ``music.play(music.NYAN)``

    :param music: music specified in `a special notation <https://microbit-micropython.readthedocs.io/en/v2-docs/music.html#musical-notation>`_
    :param pin: the output pin for use with an external speaker (default ``pin0``), ``None`` for no sound.
    :param wait: If ``wait`` is set to ``True``, this function is blocking.
    :param loop: If ``loop`` is set to ``True``, the tune repeats until ``stop`` is called or the blocking call is interrupted.

    Many built-in melodies are defined in this module.
    """
    ...

def pitch(
    frequency: int,
    duration: int = -1,
    pin: Optional[MicroBitDigitalPin] = pin0,
    wait: bool = True,
) -> None:
    """Play a note.

    Example: ``music.pitch(185, 1000)``

    :param frequency: An integer frequency
    :param duration: A millisecond duration. If negative then sound is continuous until the next call or a call to ``stop``.
    :param pin: Optional output pin (default ``pin0``).
    :param wait: If ``wait`` is set to ``True``, this function is blocking.

    For example, if the frequency is set to 440 and the length to
    1000 then we hear a standard concert A for one second.

    You can only play one pitch on one pin at any one time.
    """
    ...

def stop(pin: Optional[MicroBitDigitalPin] = pin0) -> None:
    """Stops all music playback on the built-in speaker and any pin outputting sound.

    Example: ``music.stop()``

    :param pin: An optional argument can be provided to specify a pin, e.g. ``music.stop(pin1)``.
    """

def reset() -> None:
    """Resets ticks, bpm, duration and octave to their default values.

    Example: ``music.reset()``

    Values:
    - ``ticks = 4``
    - ``bpm = 120``
    - ``duration = 4``
    - ``octave = 4``
    """
    ...
