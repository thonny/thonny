"""Show text, images and animations on the 5×5 LED display.
"""

from ..microbit import Image
from typing import Union, overload, Iterable

def get_pixel(x: int, y: int) -> int:
    """Get the brightness of the LED at column ``x`` and row ``y``.

    Example: ``display.get_pixel(0, 0)``

    :param x: The display column (0..4)
    :param y: The display row (0..4)
    :return: A number between 0 (off) and 9 (bright)
    """
    ...

def set_pixel(x: int, y: int, value: int) -> None:
    """Set the brightness of the LED at column ``x`` and row ``y``.

    Example: ``display.set_pixel(0, 0, 9)``

    :param x: The display column (0..4)
    :param y: The display row (0..4)
    :param value: The brightness between 0 (off) and 9 (bright)
    """
    ...

def clear() -> None:
    """Set the brightness of all LEDs to 0 (off).

    Example: ``display.clear()``
    """
    ...

def show(
    image: Union[str, float, int, Image, Iterable[Image]],
    delay: int = 400,
    wait: bool = True,
    loop: bool = False,
    clear: bool = False,
) -> None:
    """Shows images, letters or digits on the LED display.

    Example: ``display.show(Image.HEART)``

    When ``image`` is an image or a list of images then each image is displayed in turn.
    If ``image`` is a string or number, each letter or digit is displayed in turn.

    :param image: A string, number, image or list of images to show.
    :param delay: Each letter, digit or image is shown with ``delay`` milliseconds between them.
    :param wait: If ``wait`` is ``True``, this function will block until the animation is finished, otherwise the animation will happen in the background.
    :param loop: If ``loop`` is ``True``, the animation will repeat forever.
    :param clear: If ``clear`` is ``True``, the display will be cleared after the sequence has finished.

    The ``wait``, ``loop`` and ``clear`` arguments must be specified using their keyword.
    """
    ...

def scroll(
    text: Union[str, float, int],
    delay: int = 150,
    wait: bool = True,
    loop: bool = False,
    monospace: bool = False,
) -> None:
    """Scrolls a number or text on the LED display.

    Example: ``display.scroll('micro:bit')``

    :param text: The string to scroll. If ``text`` is an integer or float it is first converted to a string using ``str()``.
    :param delay: The ``delay`` parameter controls how fast the text is scrolling.
    :param wait: If ``wait`` is ``True``, this function will block until the animation is finished, otherwise the animation will happen in the background.
    :param loop: If ``loop`` is ``True``, the animation will repeat forever.
    :param monospace: If ``monospace`` is ``True``, the characters will all take up 5 pixel-columns in width, otherwise there will be exactly 1 blank pixel-column between each character as they scroll.

    The ``wait``, ``loop`` and ``monospace`` arguments must be specified
    using their keyword.
    """
    ...

def on() -> None:
    """Turn on the LED display.

    Example: ``display.on()``
    """
    ...

def off() -> None:
    """Turn off the LED display (disabling the display allows you to re-use the GPIO pins for other purposes).

    Example: ``display.off()``
    """
    ...

def is_on() -> bool:
    """Check whether the LED display is enabled.

    Example: ``display.is_on()``

    :return: ``True`` if the display is on, otherwise returns ``False``.
    """
    ...

def read_light_level() -> int:
    """Read the light level.

    Example: ``display.read_light_level()``

    Uses the display's LEDs in reverse-bias mode to sense the amount of light
    falling on the display.

    :return: An integer between 0 and 255 representing the light level, with larger meaning more light.
    """
    ...
