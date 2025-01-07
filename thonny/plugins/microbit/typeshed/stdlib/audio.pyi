"""Play sounds using the micro:bit (import ``audio`` for V1 compatibility).
"""

# Re-export for V1 compatibility.
from .microbit.audio import (
    is_playing as is_playing,
    play as play,
    stop as stop,
    AudioFrame as AudioFrame,
    SoundEffect as SoundEffect,
)
