"""Pins, images, sounds, temperature and volume.
"""

from typing import Any, Callable, List, Optional, Tuple, Union, overload

from _typeshed import ReadableBuffer

# V2 only
from . import accelerometer as accelerometer
from . import audio as audio
from . import compass as compass
from . import display as display
from . import i2c as i2c
from . import microphone as microphone
from . import speaker as speaker
from . import spi as spi
from . import uart as uart

def run_every(
    callback: Optional[Callable[[], None]] = None,
    days: int = 0,
    h: int = 0,
    min: int = 0,
    s: int = 0,
    ms: int = 0,
) -> Callable[[Callable[[], None]], Callable[[], None]]:
    """Schedule to run a function at the interval specified by the time arguments **V2 only**.

    Example: ``run_every(my_logging, min=5)``

    ``run_every`` can be used in two ways:

    As a Decorator - placed on top of the function to schedule. For example::

        @run_every(h=1, min=20, s=30, ms=50)
        def my_function():
            # Do something here

    As a Function - passing the callback as a positional argument. For example::

        def my_function():
            # Do something here
        run_every(my_function, s=30)

    Each argument corresponds to a different time unit and they are additive.
    So ``run_every(min=1, s=30)`` schedules the callback every minute and a half.

    When an exception is thrown inside the callback function it deschedules the
    function. To avoid this you can catch exceptions with ``try/except``.

    :param callback: Function to call at the provided interval. Omit when using as a decorator.
    :param days: Sets the day mark for the scheduling.
    :param h: Sets the hour mark for the scheduling.
    :param min: Sets the minute mark for the scheduling.
    :param s: Sets the second mark for the scheduling.
    :param ms: Sets the millisecond mark for the scheduling.
    """

def panic(n: int) -> None:
    """Enter a panic mode.

    Example: ``panic(127)``

    :param n: An arbitrary integer <= 255 to indicate a status.

    Requires restart.
    """

def reset() -> None:
    """Restart the board."""


@overload
def scale(value: float, from_: Tuple[float, float], to: Tuple[int, int]) -> int:
    """Converts a value from a range to an integer range.

    Example: ``volume = scale(accelerometer.get_x(), from_=(-2000, 2000), to=(0, 255))``

    For example, to convert an accelerometer X value to a speaker volume.

    If one of the numbers in the ``to`` parameter is a floating point
    (i.e a decimal number like ``10.0``), this function will return a
    floating point number.

        temp_fahrenheit = scale(30, from_=(0.0, 100.0), to=(32.0, 212.0))

    :param value: A number to convert.
    :param from_: A tuple to define the range to convert from.
    :param to: A tuple to define the range to convert to.
    :return: The ``value`` converted to the ``to`` range.
    """

@overload
def scale(value: float, from_: Tuple[float, float], to: Tuple[float, float]) -> float:
    """Converts a value from a range to a floating point range.

    Example: ``temp_fahrenheit = scale(30, from_=(0.0, 100.0), to=(32.0, 212.0))``

    For example, to convert temperature from a Celsius scale to Fahrenheit.

    If one of the numbers in the ``to`` parameter is a floating point
    (i.e a decimal number like ``10.0``), this function will return a
    floating point number.
    If they are both integers (i.e ``10``), it will return an integer::

        returns_int = scale(accelerometer.get_x(), from_=(-2000, 2000), to=(0, 255))

    :param value: A number to convert.
    :param from_: A tuple to define the range to convert from.
    :param to: A tuple to define the range to convert to.
    :return: The ``value`` converted to the ``to`` range.
    """

def sleep(n: float) -> None:
    """Wait for ``n`` milliseconds.

    Example: ``sleep(1000)``

    :param n: The number of milliseconds to wait

    One second is 1000 milliseconds, so::

        microbit.sleep(1000)

    will pause the execution for one second.
    """

def running_time() -> int:
    """Get the running time of the board.

    :return: The number of milliseconds since the board was switched on or restarted.
    """

def temperature() -> int:
    """Get the temperature of the micro:bit in degrees Celsius."""

def set_volume(v: int) -> None:
    """Sets the volume.

    Example: ``set_volume(127)``

    :param v: a value between 0 (low) and 255 (high).

    Out of range values will be clamped to 0 or 255.

    **V2** only.
    """
    ...

class Button:
    """The class for the buttons ``button_a`` and ``button_b``."""

    def is_pressed(self) -> bool:
        """Check if the button is pressed.

        :return: ``True`` if the specified button ``button`` is pressed, and ``False`` otherwise.
        """
        ...
    def was_pressed(self) -> bool:
        """Check if the button was pressed since the device started or the last time this method was called.

        Calling this method will clear the press state so
        that the button must be pressed again before this method will return
        ``True`` again.

        :return: ``True`` if the specified button ``button`` was pressed, and ``False`` otherwise
        """
        ...
    def get_presses(self) -> int:
        """Get the running total of button presses, and resets this total
        to zero before returning.

        :return: The number of presses since the device started or the last time this method was called
        """
        ...

button_a: Button
"""The left button ``Button`` object."""

button_b: Button
"""The right button ``Button`` object."""

class MicroBitDigitalPin:
    """A digital pin.

    Some pins support analog and touch features using the ``MicroBitAnalogDigitalPin`` and ``MicroBitTouchPin`` subclasses.
    """

    NO_PULL: int
    PULL_UP: int
    PULL_DOWN: int
    def read_digital(self) -> int:
        """Get the digital value of the pin.

        Example: ``value = pin0.read_digital()``

        :return: 1 if the pin is high, and 0 if it's low.
        """
        ...
    def write_digital(self, value: int) -> None:
        """Set the digital value of the pin.

        Example: ``pin0.write_digital(1)``

        :param value: 1 to set the pin high or 0 to set the pin low"""
        ...
    def set_pull(self, value: int) -> None:
        """Set the pull state to one of three possible values: ``PULL_UP``, ``PULL_DOWN`` or ``NO_PULL``.

        Example: ``pin0.set_pull(pin0.PULL_UP)``

        :param value: The pull state from the relevant pin, e.g. ``pin0.PULL_UP``.
        """
        ...
    def get_pull(self) -> int:
        """Get the pull state on a pin.

        Example: ``pin0.get_pull()``

        :return: ``NO_PULL``, ``PULL_DOWN``, or ``PULL_UP``

        These are set using the ``set_pull()`` method or automatically configured
        when a pin mode requires it.
        """
        ...
    def get_mode(self) -> str:
        """Returns the pin mode.

        Example: ``pin0.get_mode()``

        When a pin is used for a specific function, like
        writing a digital value, or reading an analog value, the pin mode
        changes.

        :return: ``"unused"``, ``"analog"``, ``"read_digital"``, ``"write_digital"``, ``"display"``, ``"button"``, ``"music"``, ``"audio"``, ``"touch"``, ``"i2c"``, or ``"spi"``
        """
        ...
    def write_analog(self, value: int) -> None:
        """Output a PWM signal on the pin, with the duty cycle proportional to ``value``.

        Example: ``pin0.write_analog(254)``

        :param value: An integer or a floating point number between 0 (0% duty cycle) and 1023 (100% duty).
        """
    def set_analog_period(self, period: int) -> None:
        """Set the period of the PWM signal being output to ``period`` in milliseconds.

        Example: ``pin0.set_analog_period(10)``

        :param period: The period in milliseconds with a minimum valid value of 1ms.
        """
    def set_analog_period_microseconds(self, period: int) -> None:
        """Set the period of the PWM signal being output to ``period`` in microseconds.

        Example: ``pin0.set_analog_period_microseconds(512)``

        :param period: The period in microseconds with a minimum valid value of 256µs.
        """

class MicroBitAnalogDigitalPin(MicroBitDigitalPin):
    """A pin with analog and digital features."""

    def read_analog(self) -> int:
        """Read the voltage applied to the pin.

        Example: ``pin0.read_analog()``

        :return: An integer between 0 (meaning 0V) and 1023 (meaning 3.3V).
        """

class MicroBitTouchPin(MicroBitAnalogDigitalPin):
    """A pin with analog, digital and touch features."""

    CAPACITIVE: int
    RESISTIVE: int
    def is_touched(self) -> bool:
        """Check if the pin is being touched.

        Example: ``pin0.is_touched()``

        The default touch mode for the pins on the edge connector is ``resistive``.
        The default for the logo pin **V2** is ``capacitive``.

        **Resistive touch**
        This test is done by measuring how much resistance there is between the
        pin and ground.  A low resistance gives a reading of ``True``.  To get
        a reliable reading using a finger you may need to touch the ground pin
        with another part of your body, for example your other hand.

        **Capacitive touch**
        This test is done by interacting with the electric field of a capacitor
        using a finger as a conductor. `Capacitive touch
        <https://www.allaboutcircuits.com/technical-articles/introduction-to-capacitive-touch-sensing>`_
        does not require you to make a ground connection as part of a circuit.

        :return: ``True`` if the pin is being touched with a finger, otherwise return ``False``.
        """
        ...
    def set_touch_mode(self, value: int) -> None:
        """Set the touch mode for the pin.

        Example: ``pin0.set_touch_mode(pin0.CAPACITIVE)``

        The default touch mode for the pins on the edge connector is
        ``resistive``. The default for the logo pin **V2** is ``capacitive``.

        :param value: ``CAPACITIVE`` or ``RESISTIVE`` from the relevant pin.
        """
        ...

pin0: MicroBitTouchPin
"""Pin with digital, analog and touch features."""

pin1: MicroBitTouchPin
"""Pin with digital, analog and touch features."""

pin2: MicroBitTouchPin
"""Pin with digital, analog and touch features."""

pin3: MicroBitAnalogDigitalPin
"""Pin with digital and analog features."""

pin4: MicroBitAnalogDigitalPin
"""Pin with digital and analog features."""

pin5: MicroBitDigitalPin
"""Pin with digital features."""

pin6: MicroBitDigitalPin
"""Pin with digital features."""

pin7: MicroBitDigitalPin
"""Pin with digital features."""

pin8: MicroBitDigitalPin
"""Pin with digital features."""

pin9: MicroBitDigitalPin
"""Pin with digital features."""

pin10: MicroBitAnalogDigitalPin
"""Pin with digital and analog features."""

pin11: MicroBitDigitalPin
"""Pin with digital features."""

pin12: MicroBitDigitalPin
"""Pin with digital features."""

pin13: MicroBitDigitalPin
"""Pin with digital features."""

pin14: MicroBitDigitalPin
"""Pin with digital features."""

pin15: MicroBitDigitalPin
"""Pin with digital features."""

pin16: MicroBitDigitalPin
"""Pin with digital features."""

pin19: MicroBitDigitalPin
"""Pin with digital features."""

pin20: MicroBitDigitalPin
"""Pin with digital features."""

pin_logo: MicroBitTouchPin
"""A touch sensitive logo pin on the front of the micro:bit, which by default is set to capacitive touch mode."""

pin_speaker: MicroBitAnalogDigitalPin
"""A pin to address the micro:bit speaker.

This API is intended only for use in Pulse-Width Modulation pin operations e.g. pin_speaker.write_analog(128).
"""

class Image:
    """An image to show on the micro:bit LED display.

    Given an image object it's possible to display it via the ``display`` API::

        display.show(Image.HAPPY)
    """

    HEART: Image
    """Heart image."""

    HEART_SMALL: Image
    """Small heart image."""

    HAPPY: Image
    """Happy face image."""

    SMILE: Image
    """Smiling mouth image."""

    SAD: Image
    """Sad face image."""

    CONFUSED: Image
    """Confused face image."""

    ANGRY: Image
    """Angry face image."""

    ASLEEP: Image
    """Sleeping face image."""

    SURPRISED: Image
    """Surprised face image."""

    SILLY: Image
    """Silly face image."""

    FABULOUS: Image
    """Sunglasses face image."""

    MEH: Image
    """Unimpressed face image."""

    YES: Image
    """Tick image."""

    NO: Image
    """Cross image."""

    CLOCK12: Image
    """Image with line pointing to 12 o'clock."""

    CLOCK11: Image
    """Image with line pointing to 11 o'clock."""

    CLOCK10: Image
    """Image with line pointing to 10 o'clock."""

    CLOCK9: Image
    """Image with line pointing to 9 o'clock."""

    CLOCK8: Image
    """Image with line pointing to 8 o'clock."""

    CLOCK7: Image
    """Image with line pointing to 7 o'clock."""

    CLOCK6: Image
    """Image with line pointing to 6 o'clock."""

    CLOCK5: Image
    """Image with line pointing to 5 o'clock."""

    CLOCK4: Image
    """Image with line pointing to 4 o'clock."""

    CLOCK3: Image
    """Image with line pointing to 3 o'clock."""

    CLOCK2: Image
    """Image with line pointing to 2 o'clock."""

    CLOCK1: Image
    """Image with line pointing to 1 o'clock."""

    ARROW_N: Image
    """Image of arrow pointing north."""

    ARROW_NE: Image
    """Image of arrow pointing north east."""

    ARROW_E: Image
    """Image of arrow pointing east."""

    ARROW_SE: Image
    """Image of arrow pointing south east."""

    ARROW_S: Image
    """Image of arrow pointing south."""

    ARROW_SW: Image
    """Image of arrow pointing south west."""

    ARROW_W: Image
    """Image of arrow pointing west."""

    ARROW_NW: Image
    """Image of arrow pointing north west."""

    TRIANGLE: Image
    """Image of a triangle pointing up."""

    TRIANGLE_LEFT: Image
    """Image of a triangle in the left corner."""

    CHESSBOARD: Image
    """Alternate LEDs lit in a chessboard pattern."""

    DIAMOND: Image
    """Diamond image."""

    DIAMOND_SMALL: Image
    """Small diamond image."""

    SQUARE: Image
    """Square image."""

    SQUARE_SMALL: Image
    """Small square image."""

    RABBIT: Image
    """Rabbit image."""

    COW: Image
    """Cow image."""

    MUSIC_CROTCHET: Image
    """Crotchet note image."""

    MUSIC_QUAVER: Image
    """Quaver note image."""

    MUSIC_QUAVERS: Image
    """Pair of quavers note image."""

    PITCHFORK: Image
    """Pitchfork image."""

    XMAS: Image
    """Christmas tree image."""

    PACMAN: Image
    """Pac-Man arcade character image."""

    TARGET: Image
    """Target image."""

    TSHIRT: Image
    """T-shirt image."""

    ROLLERSKATE: Image
    """Rollerskate image."""

    DUCK: Image
    """Duck image."""

    HOUSE: Image
    """House image."""

    TORTOISE: Image
    """Tortoise image."""

    BUTTERFLY: Image
    """Butterfly image."""

    STICKFIGURE: Image
    """Stick figure image."""

    GHOST: Image
    """Ghost image."""

    SWORD: Image
    """Sword image."""

    GIRAFFE: Image
    """Giraffe image."""

    SKULL: Image
    """Skull image."""

    UMBRELLA: Image
    """Umbrella image."""

    SNAKE: Image
    """Snake image."""

    SCISSORS: Image
    """Scissors image."""

    ALL_CLOCKS: List[Image]
    """A list containing all the CLOCK_ images in sequence."""

    ALL_ARROWS: List[Image]
    """A list containing all the ARROW_ images in sequence."""
    @overload
    def __init__(self, string: str) -> None:
        """Create an image from a string describing which LEDs are lit.

        ``string`` has to consist of digits 0-9 arranged into lines,
        describing the image, for example::

            image = Image("90009:"
                          "09090:"
                          "00900:"
                          "09090:"
                          "90009")

        will create a 5×5 image of an X. The end of a line is indicated by a
        colon. It's also possible to use newlines (\\n) insead of the colons.

        :param string: The string describing the image.
        """
        ...
    @overload
    def __init__(
        self, width: int = 5, height: int = 5, buffer: ReadableBuffer = None
    ) -> None:
        """Create an empty image with ``width`` columns and ``height`` rows.

        :param width: Optional width of the image
        :param height: Optional height of the image
        :param buffer: Optional array or bytes of ``width``×``height`` integers in range 0-9 to initialize the image

        Examples::

            Image(2, 2, b'\x08\x08\x08\x08')
            Image(2, 2, bytearray([9,9,9,9]))

        These create 2 x 2 pixel images at full brightness.
        """
        ...
    def width(self) -> int:
        """Get the number of columns.

        :return: The number of columns in the image
        """
        ...
    def height(self) -> int:
        """Get the number of rows.

        :return: The number of rows in the image
        """
        ...
    def set_pixel(self, x: int, y: int, value: int) -> None:
        """Set the brightness of a pixel.

        Example: ``my_image.set_pixel(0, 0, 9)``

        :param x: The column number
        :param y: The row number
        :param value: The brightness as an integer between 0 (dark) and 9 (bright)

        This method will raise an exception when called on any of the built-in
        read-only images, like ``Image.HEART``.
        """
        ...
    def get_pixel(self, x: int, y: int) -> int:
        """Get the brightness of a pixel.

        Example: ``my_image.get_pixel(0, 0)``

        :param x: The column number
        :param y: The row number
        :return: The brightness as an integer between 0 and 9.
        """
        ...
    def shift_left(self, n: int) -> Image:
        """Create a new image by shifting the picture left.

        Example: ``Image.HEART_SMALL.shift_left(1)``

        :param n: The number of columns to shift by
        :return: The shifted image
        """
        ...
    def shift_right(self, n: int) -> Image:
        """Create a new image by shifting the picture right.

        Example: ``Image.HEART_SMALL.shift_right(1)``

        :param n: The number of columns to shift by
        :return: The shifted image
        """
        ...
    def shift_up(self, n: int) -> Image:
        """Create a new image by shifting the picture up.

        Example: ``Image.HEART_SMALL.shift_up(1)``

        :param n: The number of rows to shift by
        :return: The shifted image
        """
        ...
    def shift_down(self, n: int) -> Image:
        """Create a new image by shifting the picture down.

        Example: ``Image.HEART_SMALL.shift_down(1)``

        :param n: The number of rows to shift by
        :return: The shifted image
        """
        ...
    def crop(self, x: int, y: int, w: int, h: int) -> Image:
        """Create a new image by cropping the picture.

        Example: ``Image.HEART.crop(1, 1, 3, 3)``

        :param x: The crop offset column
        :param y: The crop offset row
        :param w: The crop width
        :param h: The crop height
        :return: The new image
        """
        ...
    def copy(self) -> Image:
        """Create an exact copy of the image.

        Example: ``Image.HEART.copy()``

        :return: The new image
        """
        ...
    def invert(self) -> Image:
        """Create a new image by inverting the brightness of the pixels in the
        source image.

        Example: ``Image.SMALL_HEART.invert()``

        :return: The new image.
        """
        ...
    def fill(self, value: int) -> None:
        """Set the brightness of all the pixels in the image.

        Example: ``my_image.fill(5)``

        :param value: The new brightness as a number between 0 (dark) and 9 (bright).

        This method will raise an exception when called on any of the built-in
        read-only images, like ``Image.HEART``.
        """
        ...
    def blit(
        self,
        src: Image,
        x: int,
        y: int,
        w: int,
        h: int,
        xdest: int = 0,
        ydest: int = 0,
    ) -> None:
        """Copy an area from another image into this image.

        Example: ``my_image.blit(Image.HEART, 1, 1, 3, 3, 1, 1)``

        :param src: The source image
        :param x: The starting column offset in the source image
        :param y: The starting row offset in the source image
        :param w: The number of columns to copy
        :param h: The number of rows to copy
        :param xdest: The column offset to modify in this image
        :param ydest: The row offset to modify in this image

        Pixels outside the source image are treated as having a brightness of 0.

        ``shift_left()``, ``shift_right()``, ``shift_up()``, ``shift_down()``
        and ``crop()`` can are all implemented by using ``blit()``.

        For example, img.crop(x, y, w, h) can be implemented as::

            def crop(self, x, y, w, h):
                res = Image(w, h)
                res.blit(self, x, y, w, h)
                return res
        """
        ...
    def __repr__(self) -> str:
        """Get a compact string representation of the image."""
        ...
    def __str__(self) -> str:
        """Get a readable string representation of the image."""
        ...
    def __add__(self, other: Image) -> Image:
        """Create a new image by adding the brightness values from the two
        images for each pixel.

        Example: ``Image.HEART + Image.HAPPY``

        :param other: The image to add.
        """
        ...
    def __sub__(self, other: Image) -> Image:
        """Create a new image by subtracting the brightness values of the
        other image from this image.

        Example: ``Image.HEART - Image.HEART_SMALL``

        :param other: The image to subtract.
        """
        ...
    def __mul__(self, n: float) -> Image:
        """Create a new image by multiplying the brightness of each pixel by
        ``n``.

        Example: ``Image.HEART * 0.5``

        :param n: The value to multiply by.
        """
        ...
    def __truediv__(self, n: float) -> Image:
        """Create a new image by dividing the brightness of each pixel by
        ``n``.

        Example: ``Image.HEART / 2``

        :param n: The value to divide by.
        """
        ...

class SoundEvent:
    LOUD: SoundEvent
    """Represents the transition of sound events, from ``quiet`` to ``loud`` like clapping or shouting."""

    QUIET: SoundEvent
    """Represents the transition of sound events, from ``loud`` to ``quiet`` like speaking or background music."""

class Sound:
    """The built-in sounds can be called using ``audio.play(Sound.NAME)``."""

    GIGGLE: Sound
    """Giggling sound."""

    HAPPY: Sound
    """Happy sound."""

    HELLO: Sound
    """Greeting sound."""

    MYSTERIOUS: Sound
    """Mysterious sound."""

    SAD: Sound
    """Sad sound."""

    SLIDE: Sound
    """Sliding sound."""

    SOARING: Sound
    """Soaring sound."""

    SPRING: Sound
    """Spring sound."""

    TWINKLE: Sound
    """Twinkling sound."""

    YAWN: Sound
    """Yawning sound."""
