"""Play sounds using the micro:bit (import ``audio`` for V1 compatibility).
"""

# Re-export for V1 compatibility.
from .microbit.audio import AudioFrame as AudioFrame
from .microbit.audio import SoundEffect as SoundEffect
from .microbit.audio import is_playing as is_playing
from .microbit.audio import play as play
from .microbit.audio import stop as stop
