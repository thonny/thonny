###########################
# neopixel
from typing import Tuple

class _NeoPixelBase:
    """
    a class to add a few missing methods to the NeoPixel class
    """

    def __len__(self) -> int:
        """
        Returns the number of LEDs in the strip.
        """
        ...

    def __setitem__(self, index: int, val, /) -> None:
        """
        Set the pixel at *index* to the value, which is an RGB/RGBW tuple.
        """
        ...

    def __getitem__(self, index: int, /) -> Tuple:
        """
        Returns the pixel at *index* as an RGB/RGBW tuple.
        """
        ...
