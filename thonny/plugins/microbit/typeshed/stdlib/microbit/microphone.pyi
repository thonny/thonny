"""Respond to sound using the built-in microphone (V2 only).
"""

from typing import Optional, Tuple
from ..microbit import SoundEvent

def current_event() -> Optional[SoundEvent]:
    """Get the last recorded sound event

    Example: ``microphone.current_event()``

    :return: The event, ``SoundEvent('loud')`` or ``SoundEvent('quiet')``.
    """
    ...

def was_event(event: SoundEvent) -> bool:
    """Check if a sound was heard at least once since the last call.

    Example: ``microphone.was_event(SoundEvent.LOUD)``

    This call clears the sound history before returning.

    :param event: The event to check for,  such as ``SoundEvent.LOUD`` or ``SoundEvent.QUIET``
    :return: ``True`` if sound was heard at least once since the last call, otherwise ``False``.
    """
    ...

def is_event(event: SoundEvent) -> bool:
    """Check the most recent sound event detected.

    Example: ``microphone.is_event(SoundEvent.LOUD)``

    This call does not clear the sound event history.

    :param event: The event to check for,  such as ``SoundEvent.LOUD`` or ``SoundEvent.QUIET``
    :return: ``True`` if sound was the most recent heard, ``False`` otherwise.
    """
    ...

def get_events() -> Tuple[SoundEvent, ...]:
    """Get the sound event history as a tuple.

    Example: ``microphone.get_events()``

    This call clears the sound history before returning.

    :return: A tuple of the event history with the most recent event last.
    """
    ...

def set_threshold(event: SoundEvent, value: int) -> None:
    """Set the threshold for a sound event.

    Example: ``microphone.set_threshold(SoundEvent.LOUD, 250)``

    A high threshold means the event will only trigger if the sound is very loud (>= 250 in the example).

    :param event: A sound event, such as ``SoundEvent.LOUD`` or ``SoundEvent.QUIET``.
    :param value: The threshold level in the range 0-255.
    """
    ...

def sound_level() -> int:
    """Get the sound pressure level.

    Example: ``microphone.sound_level()``

    :return: A representation of the sound pressure level in the range 0 to 255.
    """
    ...
