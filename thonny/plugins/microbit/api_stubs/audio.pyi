from typing import Iterable, Tuple

from microbit import _MicroBitAnalogDigitalPin

class AudioFrame(list):
    """
    Represents a list of 32 samples each of which is a signed byte.
    It takes just over 4ms to play a single frame.
    """
    def copyfrom(self, other) -> None:
        pass



def play(
    source: Iterable[AudioFrame],
    wait: bool = True,
    pin: _MicroBitAnalogDigitalPin = ...,
    return_pin: _MicroBitAnalogDigitalPin = None
) -> None:
    """
    Play the source to completion.

    `source`: `Sound` - The microbit module contains a list of built-in sounds that your can pass to
    audio.play(). The source agrument can also be an iterable of AudioFrame elements as described below.

    If `wait` is True, this function will block until the source is exhausted.

    `pin` An optional argument to specify the output pin can be used to override the default of
    pin0. If we do not want any sound to play we can use pin=None.

    `return_pin`: specifies a differential edge connector pin to connect to an external speaker
    instead of ground. This is ignored for the V2 revision.
    """


def is_playing() -> bool:
    """
    Return True if audio is playing, otherwise return False.
    """


def stop() -> None:
    """
    Stops all audio playback.
    """
