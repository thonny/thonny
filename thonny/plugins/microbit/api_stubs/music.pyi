"""
MicroPython on the BBC micro:bit comes with a powerful music and
sound module. It’s very easy to generate bleeps and bloops from
the device if you attach a speaker. Use crocodile clips to attach
pin 0 and GND to the positive and negative inputs on the speaker -
it doesn’t matter which way round they are connected to the speaker.

Musical Notation

    An individual note is specified thus:

    NOTE[octave][:duration]

    For example, A1:4 refers to the note “A” in octave 1 that lasts for four ticks
     (a tick is an arbitrary length of time defined by a tempo setting function -
     see below). If the note name R is used then it is treated as a rest (silence).

    Accidentals (flats and sharps) are denoted by the b
    (flat - a lower case b) and # (sharp - a hash symbol).
    For example, Ab is A-flat and C# is C-sharp.

    Note names are case-insensitive.

    The octave and duration parameters are states that carry over to
    subsequent notes until re-specified. The default states are octave = 4
    (containing middle C) and duration = 4 (a crotchet, given the default
    tempo settings - see below).

    For example, if 4 ticks is a crotchet, the following list is crotchet,
    quaver, quaver, crotchet based arpeggio:

    ['c1:4', 'e:2', 'g', 'c2:4']

    The opening of Beethoven’s 5th Symphony would be encoded thus:

    ['r4:2', 'g', 'g', 'g', 'eb:8', 'r:2', 'f', 'f', 'f', 'd:8']

    The definition and scope of an octave conforms to the table
    listed on this page about scientific pitch notation. For example, middle “C” is
    c4' and concert “A” (440) is 'a4'. Octaves start on the note “C”.
    The definition and scope of an octave conforms to the table
    listed on this page about scientific pitch notation. For example, middle
    “C” is 'c4' and concert “A” (440) is 'a4'. Octaves start on the note “C”.


        Built in Melodies

        For the purposes of education and entertainment, the module contains
        several example tunes that are expressed as Python lists. They can be used like this:

     import music
     music.play(music.NYAN)


    All the tunes are either out of copyright, composed by
    Nicholas H.Tollervey and
    released to the public domain or have an unknown composer and are
    covered by a fair (educational) use provision.

    They are:

    DADADADUM - the opening to Beethoven’s 5th Symphony in C minor.
    ENTERTAINER - the opening fragment of Scott Joplin’s
                  Ragtime classic “The Entertainer”.
    PRELUDE - the opening of the first Prelude in C Major of
              J.S.Bach’s 48 Preludes and Fugues.
    ODE - the “Ode to Joy” theme from Beethoven’s 9th Symphony in D minor.
    NYAN - the Nyan Cat theme (http://www.nyan.cat/). The composer is unknown.
           This is fair use for educational porpoises (as they say in New York).
    RINGTONE - something that sounds like a mobile phone ringtone. To be used
               to indicate an incoming message.
    FUNK - a funky bass line for secret agents and criminal masterminds.
    BLUES - a boogie-woogie 12-bar blues walking bass.
    BIRTHDAY - “Happy Birthday to You...” for copyright status see:
                http://www.bbc.co.uk/news/world-us-canada-34332853
    WEDDING - the bridal chorus from Wagner’s opera “Lohengrin”.
    FUNERAL - the “funeral march” otherwise known as Frédéric Chopin’s
            Piano Sonata No. 2 in B♭ minor, Op. 35.
    PUNCHLINE - a fun fragment that signifies a joke has been made.
    PYTHON - John Philip Sousa’s march “Liberty Bell” aka, the theme for
             “Monty Python’s Flying Circus” (after which the Python
            programming language is named).
    BADDY - silent movie era entrance of a baddy.
    CHASE - silent movie era chase scene.
    BA_DING - a short signal to indicate something has happened.
    WAWAWAWAA - a very sad trombone.
    JUMP_UP - for use in a game, indicating upward movement.
    JUMP_DOWN - for use in a game, indicating downward movement.
    POWER_UP - a fanfare to indicate an achievement unlocked.
    POWER_DOWN - a sad fanfare to indicate an achievement lost.

    Example

        Plays a simple tune using the Micropython music module.
        This example requires a speaker/buzzer/headphones connected to P0 and GND.

    from microbit import *
    import music

    # play Prelude in C.
    notes = [
        'c4:1', 'e', 'g', 'c5', 'e5', 'g4', 'c5', 'e5', 'c4', 'e', 'g', 'c5', 'e5', 'g4', 'c5', 'e5',
        'c4', 'd', 'g', 'd5', 'f5', 'g4', 'd5', 'f5', 'c4', 'd', 'g', 'd5', 'f5', 'g4', 'd5', 'f5',
        'b3', 'd4', 'g', 'd5', 'f5', 'g4', 'd5', 'f5', 'b3', 'd4', 'g', 'd5', 'f5', 'g4', 'd5', 'f5',
        'c4', 'e', 'g', 'c5', 'e5', 'g4', 'c5', 'e5', 'c4', 'e', 'g', 'c5', 'e5', 'g4', 'c5', 'e5',
        'c4', 'e', 'a', 'e5', 'a5', 'a4', 'e5', 'a5', 'c4', 'e', 'a', 'e5', 'a5', 'a4', 'e5', 'a5',
        'c4', 'd', 'f#', 'a', 'd5', 'f#4', 'a', 'd5', 'c4', 'd', 'f#', 'a', 'd5', 'f#4', 'a', 'd5',
        'b3', 'd4', 'g', 'd5', 'g5', 'g4', 'd5', 'g5', 'b3', 'd4', 'g', 'd5', 'g5', 'g4', 'd5', 'g5',
        'b3', 'c4', 'e', 'g', 'c5', 'e4', 'g', 'c5', 'b3', 'c4', 'e', 'g', 'c5', 'e4', 'g', 'c5',
        'b3', 'c4', 'e', 'g', 'c5', 'e4', 'g', 'c5', 'b3', 'c4', 'e', 'g', 'c5', 'e4', 'g', 'c5',
        'a3', 'c4', 'e', 'g', 'c5', 'e4', 'g', 'c5', 'a3', 'c4', 'e', 'g', 'c5', 'e4', 'g', 'c5',
        'd3', 'a', 'd4', 'f#', 'c5', 'd4', 'f#', 'c5', 'd3', 'a', 'd4', 'f#', 'c5', 'd4', 'f#', 'c5',
        'g3', 'b', 'd4', 'g', 'b', 'd', 'g', 'b', 'g3', 'b3', 'd4', 'g', 'b', 'd', 'g', 'b'
    ]

    music.play(notes)
    """
from typing import List, Tuple, Union

from .microbit import MicroBitAnalogDigitalPin, pin0

DADADADUM = 0
ENTERTAINER = 1
PRELUDE = 2
ODE = 3
NYAN = 4
RINGTONE = 5
FUNK = 6
BLUES = 7
BIRTHDAY = 8
WEDDING = 9
FUNERAL = 10
PUNCHLINE = 11
PYTHON = 12
BADDY = 12
CHASE = 13
BA_DING = 14
WAWAWAWAA = 15
JUMP_UP = 16
JUMP_DOWN = 17
POWER_UP = 18
POWER_DOWN = 19


def set_tempo(ticks: int = 4, bpm: int = 120) -> None:
    """
    Sets the approximate tempo for playback.

    A number of ticks (expressed as an integer) constitute a beat.
    Each beat is to be played at a certain frequency per minute
    (expressed as the more familiar BPM - beats per minute -
     also as an integer).

    Suggested default values allow the following useful behaviour:

        music.set_tempo() - reset the tempo to default of ticks = 4, bpm = 120
        music.set_tempo(ticks=8) - change the “definition” of a beat
        music.set_tempo(bpm=180) - just change the tempo

    To work out the length of a tick in milliseconds is very simple arithmetic:
    60000/bpm/ticks_per_beat . For the default values that’s
    60000/120/4 = 125 milliseconds or 1 beat = 500 milliseconds.
    """


def get_tempo(self) -> Tuple[int, int]:
    """
    Gets the current tempo as a tuple of integers: (ticks, bpm).
    """


def play(music: Union[str, List[str]],
         pin: MicroBitAnalogDigitalPin = pin0, wait: bool=True, loop: bool=False) -> None:
    """
    Sets the approximate tempo for playback.

    A number of ticks (expressed as an integer) constitute a beat.
    Each beat is to be played at a certain frequency per
    minute (expressed as the more familiar BPM - beats per minute -
    also as an integer).

    Suggested default values allow the following useful behaviour:

        music.set_tempo() - reset the tempo to default of ticks = 4, bpm = 120
        music.set_tempo(ticks=8) - change the “definition” of a beat
        music.set_tempo(bpm=180) - just change the tempo

    To work out the length of a tick in milliseconds is very simple arithmetic:
    60000/bpm/ticks_per_beat . For the default values that’s 60000/120/4 =
    125 milliseconds or 1 beat = 500 milliseconds.
    """


def pitch(frequency: int, len=-1, pin: MicroBitAnalogDigitalPin = pin0,
          wait: bool=True) -> None:
    """

    Plays a pitch at the integer frequency given for the specified
    number of milliseconds. For example, if the frequency is set to 440 and
    the length to 1000 then we hear a standard concert A for one second.

    If wait is set to True, this function is blocking.

    If len is negative the pitch is played continuously until
    either the blocking call is interrupted or, in the case of a background call,
    a new frequency is set or stop is called (see below).
    """


def stop(pin: MicroBitAnalogDigitalPin = pin0) -> None:
    """
    Stops all music playback on a given pin.
    """


def reset() -> None:
    """
    Resets the state of the following attributes in the following way:

            ticks = 4
            bpm = 120
            duration = 4
            octave = 4
    """
