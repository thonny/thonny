"""
PlaySound(sound, flags) - play a sound
SND_FILENAME - sound is a wav file name
SND_ALIAS - sound is a registry sound association name
SND_LOOP - Play the sound repeatedly; must also specify SND_ASYNC
SND_MEMORY - sound is a memory image of a wav file
SND_PURGE - stop all instances of the specified sound
SND_ASYNC - PlaySound returns immediately
SND_NODEFAULT - Do not play a default beep if the sound can not be found
SND_NOSTOP - Do not interrupt any sounds currently playing
SND_NOWAIT - Return immediately if the sound driver is busy

Beep(frequency, duration) - Make a beep through the PC speaker.
MessageBeep(type) - Call Windows MessageBeep.
"""

import sys
from _typeshed import ReadableBuffer
from typing import Final, Literal, overload

if sys.platform == "win32":
    SND_APPLICATION: Final = 128
    SND_FILENAME: Final = 131072
    SND_ALIAS: Final = 65536
    SND_LOOP: Final = 8
    SND_MEMORY: Final = 4
    SND_PURGE: Final = 64
    SND_ASYNC: Final = 1
    SND_NODEFAULT: Final = 2
    SND_NOSTOP: Final = 16
    SND_NOWAIT: Final = 8192

    MB_ICONASTERISK: Final = 64
    MB_ICONEXCLAMATION: Final = 48
    MB_ICONHAND: Final = 16
    MB_ICONQUESTION: Final = 32
    MB_OK: Final = 0
    def Beep(frequency: int, duration: int) -> None: ...
    # Can actually accept anything ORed with 4, and if not it's definitely str, but that's inexpressible
    @overload
    def PlaySound(sound: ReadableBuffer | None, flags: Literal[4]) -> None: ...
    @overload
    def PlaySound(sound: str | ReadableBuffer | None, flags: int) -> None: ...
    def MessageBeep(type: int = 0) -> None: ...
