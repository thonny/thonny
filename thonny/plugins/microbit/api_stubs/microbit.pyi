# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from typing import Final, List, NoReturn, Optional, Tuple, Union, overload

import audio  # this module is available via microbit since V2

def panic(n: Optional[int]=...) -> NoReturn:
    """
    Enter a panic mode. Requires restart. Pass in an arbitrary integer <= 255 to indicate a status.
    """
    pass


def sleep(time: Union[int, float]) -> None:
    """
    Wait for n milliseconds. One second is 1000 milliseconds, so:

        microbit.sleep(1000)

    will pause the execution for one second. n can be an integer or a floating point number.
    """
    pass

def reset() -> NoReturn:
    """
    Restart the board.
    """

def running_time() -> int:
    """
    Return the number of milliseconds since the board was switched on or restarted.
    """
    pass


def temperature() -> int:
    """
    Return the temperature of the micro:bit in degrees Celcius.
    """
    pass

# Image
class Image(object):
    @overload
    def __init__(self, image: str) -> None:
        """
        String must contain digits 0-9 arranged into lines, describing the image, for example:

            image = Image("90009:"
                          "09090:"
                          "00900:"
                          "09090:"
                          "90009")

        will create a 5×5 image of an X. The end of a line is indicated by a colon.

        It’s also possible to use a newline (n) to indicate the end of a line like this:

            image = Image("90009\n"
                          "09090\n"
                          "00900\n"
                          "09090\n"
                          "90009")
        """

    @overload
    def __init__(self, width=None, height=None, buffer=None) -> None:
        """
        Create empty image with width columns and height rows. Optionally buffer can be an array
        of width x height integers in range 0-9 to initialize the image:

            Image(2, 2, b'\x08\x08\x08\x08')

        or:

            Image(2, 2, bytearray([9,9,9,9]))

        Will create a 2 x 2 pixel image at full brightness.
        """

    def width(self) -> int:
        """
        Return the width of the image in pixels.
        """
        pass

    def height(self) -> int:
        """
        Return the height of the image in pixels.
        """
        pass

    def get_pixel(self, x: int, y: int) -> int:
        """
        Return the brightness of pixel at column x and row y as an integer between 0 and 9.
        """
        pass

    def set_pixel(self, x: int, y: int, b: int) -> None:
        """
        Set the brightness of the pixel at column x and row y to the value, which has to be between
        0 (dark) and 9 (bright).

        This method will raise an exception when called on any of the built-in read-only images,
        like Image.HEART.
        """
        pass

    def shift_left(self, n: int) -> 'Image':
        """
        Return a new image created by shifting the picture left by n columns.
        """
        pass

    def shift_right(self, n: int) -> 'Image':
        """
        Same as image.shift_left(-n).
        """
        pass

    def shift_up(self, n: int) -> 'Image':
        """
        Return a new image created by shifting the picture up by n rows.
        """
        pass

    def shift_down(self, n: int) -> 'Image':
        """
        Same as image.shift_up(-n).
        """
        pass

    def copy(self) -> 'Image':
        """
        Return an exact copy of the image.
        """
        pass

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> 'Image':
        """
        Return a new image by cropping the picture to a width of w and a height of h, starting with
        the pixel at column x and row y.
        """
        pass

    def invert(self) -> 'Image':
        """
        Return a new image by inverting the brightness of the pixels in the source image.
        """
        pass

    def fill(self, value) -> None:
        """
        Set the brightness of all the pixels in the image to the value, which has to be between 0
        (dark) and 9 (bright).

        This method will raise an exception when called on any of the built-in read-only images,
        like Image.HEART.
        """

    def blit(self, src: "Image", x: int, y: int, w: int, h: int, xdest=0, ydest=0) -> None:
        """
        Copy the rectangle defined by x, y, w, h from the image src into this image at xdest, ydest.
        Areas in the source rectangle, but outside the source image are treated as having a value of 0.

        shift_left(), shift_right(), shift_up(), shift_down() and crop() can are all implemented by using blit(). For example, img.crop(x, y, w, h) can be implemented as:

            def crop(self, x, y, w, h):
                res = Image(w, h)
                res.blit(self, x, y, w, h)
                return res
        """

    def __add__(self, other: "Image") -> "Image":
        """Create a new image by adding the brightness values from the two images for each pixel."""

    def __mul__(self, n: int) -> "Image":
        """
        Create a new image by multiplying the brightness of each pixel by n.
        """

    HEART : "Image" = ...
    HEART_SMALL : "Image" = ...
    HAPPY : "Image" = ...
    SMILE : "Image" = ...
    SAD : "Image" = ...
    CONFUSED : "Image" = ...
    ANGRY : "Image" = ...
    ASLEEP : "Image" = ...
    SURPRISED : "Image" = ...
    SILLY : "Image" = ...
    FABULOUS : "Image" = ...
    MEH : "Image" = ...
    YES : "Image" = ...
    NO : "Image" = ...
    CLOCK12 : "Image" = ...
    CLOCK11 : "Image" = ...
    CLOCK10 : "Image" = ...
    CLOCK9 : "Image" = ...
    CLOCK8 : "Image" = ...
    CLOCK7 : "Image" = ...
    CLOCK6 : "Image" = ...
    CLOCK5 : "Image" = ...
    CLOCK4 : "Image" = ...
    CLOCK3 : "Image" = ...
    CLOCK2 : "Image" = ...
    CLOCK1 : "Image" = ...
    ARROW_N : "Image" = ...
    ARROW_NE : "Image" = ...
    ARROW_E : "Image" = ...
    ARROW_SE : "Image" = ...
    ARROW_S : "Image" = ...
    ARROW_SW : "Image" = ...
    ARROW_W : "Image" = ...
    ARROW_NW : "Image" = ...
    TRIANGLE : "Image" = ...
    TRIANGLE_LEFT : "Image" = ...
    CHESSBOARD : "Image" = ...
    DIAMOND : "Image" = ...
    DIAMOND_SMALL : "Image" = ...
    SQUARE : "Image" = ...
    SQUARE_SMALL : "Image" = ...
    RABBIT : "Image" = ...
    COW : "Image" = ...
    MUSIC_CROTCHET : "Image" = ...
    MUSIC_QUAVER : "Image" = ...
    MUSIC_QUAVERS : "Image" = ...
    PITCHFORK : "Image" = ...
    XMAS : "Image" = ...
    PACMAN : "Image" = ...
    TARGET : "Image" = ...
    TSHIRT : "Image" = ...
    ROLLERSKATE : "Image" = ...
    DUCK : "Image" = ...
    HOUSE : "Image" = ...
    TORTOISE : "Image" = ...
    BUTTERFLY : "Image" = ...
    STICKFIGURE : "Image" = ...
    GHOST : "Image" = ...
    SWORD : "Image" = ...
    GIRAFFE : "Image" = ...
    SKULL : "Image" = ...
    UMBRELLA : "Image" = ...
    SNAKE : "Image" = ...

    ALL_CLOCKS: List["Image"] = ...
    ALL_ARROWS: List["Image"] = ...




# Accelerometer 3D orientation
class _MicroBitAccelerometer(object):
    """
    This object gives you access to the on-board accelerometer. The accelerometer also provides
    convenience functions for detecting gestures. The recognised gestures are: up, down, left, right,
    face up, face down, freefall, 3g, 6g, 8g, shake.

    By default MicroPython sets the accelerometer range to +/- 2g, changing the accelerometer range
    is currently not possible in MicroPython. The accelerometer returns a value in the range 0..1024
    for each axis, which is then scaled accordingly.
    """
    def get_x(self) -> int:
        """
        Get the acceleration measurement (tilt) in the x axis, as a positive or negative integer, depending
        on the direction. The measurement is given in milli-g. By default the accelerometer is
        configured with a range of +/- 2g, and so this method will return within the range of +/- 2000mg.
        """
        pass

    def get_y(self) -> int:
        """
        Get the acceleration measurement (tilt) in the y axis, as a positive or negative integer, depending
        on the direction. The measurement is given in milli-g. By default the accelerometer is
        configured with a range of +/- 2g, and so this method will return within the range of +/- 2000mg.
        """
        pass

    def get_z(self) -> int:
        """
        Get the acceleration measurement in the z axis (up-down motion), as a positive or negative integer, depending
        on the direction. The measurement is given in milli-g. By default the accelerometer is
        configured with a range of +/- 2g, and so this method will return within the range of +/- 2000mg.
        """
        pass

    def get_values(self) -> Tuple[int, int, int]:
        """
        Get the acceleration measurements in all axes at once, as a three-element tuple of integers
        ordered as X, Y, Z. By default the accelerometer is configured with a range of +/- 2g, and
        so X, Y, and Z will be within the range of +/-2000mg.
        """

    def current_gesture(self) -> str:
        """
        Return the name of the current gesture.

        MicroPython understands the following gesture names: "up", "down", "left", "right", "face up",
        "face down", "freefall", "3g", "6g", "8g", "shake". Gestures are always represented as strings.

        No gesture is expressed as "".
        """

    def is_gesture(self, name: str) -> bool:
        """
        Return True or False to indicate if the named gesture is currently
        active.
        MicroPython understands the following gestures: 'up', 'down', 'left',
        'right', 'face up', 'face down', 'freefall', '3g', '6g', '8g' and
        'shake'.
        """
        pass

    def was_gesture(self, name: str) -> bool:
        """
        Return True or False to indicate if the named gesture was active since
        the last call.
        MicroPython understands the following gestures: 'up', 'down', 'left',
        'right', 'face up', 'face down', 'freefall', '3g', '6g', '8g' and
        'shake'.
        """
        pass

    def get_gestures(self) -> Tuple[str, ...]:
        """
        Return a tuple indicating the gesture history. The most recent gesture
        is last.
        Calling this method also clears the gesture history.
        MicroPython understands the following gestures: 'up', 'down', 'left',
        'right', 'face up', 'face down', 'freefall', '3g', '6g', '8g' and
        'shake'.
        """
        pass


accelerometer : _MicroBitAccelerometer = ...


# Pushbutton
class _MicroBitButton(object):
    def is_pressed(self) -> bool:
        """
        Returns True if the this button is currently being held down, and False otherwise.
        """
        pass

    def was_pressed(self) -> bool:
        """
        Returns True or False to indicate if the button was pressed (went from up to down) since the
        device started or the last time this method was called. Calling this method will clear the
        press state so that the button must be pressed again before this method will return True again.
        """
        pass

    def get_presses(self) -> int:
        """
        Returns the running total of button presses, and resets this total to zero before returning.
        """
        pass


button_a : _MicroBitButton = ...
button_b : _MicroBitButton = ...


# Compass 3D direction heading
class _MicroBitCompass(object):
    def is_calibrated(self) -> bool:
        """
        Returns True if the compass has been successfully calibrated, and returns False otherwise.
        """
        pass

    def calibrate(self) -> None:
        """
        Starts the calibration process. An instructive message will be scrolled to the user after
        which they will need to rotate the device in order to draw a circle on the LED display.
        """
        pass

    def clear_calibration(self) -> None:
        """
        Undoes the calibration, making the compass uncalibrated again.
        """
        pass

    def get_x(self) -> int:
        """
        Gives the reading of the magnetic field strength on the x axis in nano tesla, as a positive
        or negative integer, depending on the direction of the field.
        """
        pass

    def get_y(self) -> int:
        """
        Gives the reading of the magnetic field strength on the y axis in nano tesla, as a positive
        or negative integer, depending on the direction of the field.
        """
        pass

    def get_z(self) -> int:
        """
        Gives the reading of the magnetic field strength on the z axis in nano tesla, as a positive
        or negative integer, depending on the direction of the field.
        """
        pass

    def get_field_strength(self) -> int:
        """
        Returns an integer indication of the magnitude of the magnetic field around the device in nano tesla.
        """
        pass

    def heading(self) -> int:
        """
        Gives the compass heading, calculated from the above readings, as an integer in the range
        from 0 to 360, representing the angle in degrees, clockwise, with north as 0.
        """
        pass


compass : _MicroBitCompass = ...


# Display 5x5 LED grid
class _MicroBitDisplay(object):
    """
    This module controls the 5×5 LED display on the front of your board. It can be used to display
    images, animations and even text.
    """

    def get_pixel(self, x: int, y: int) -> int:
        """
        Return the brightness of the LED at column x and row y as an integer between 0 (off) and 9 (bright).
        """
        pass

    def set_pixel(self, x: int, y: int, value: int) -> None:
        """
        Set the brightness of the LED at column x and row y to value, which has to be an integer between 0 and 9.
        """
        pass

    def clear(self) -> None:
        """
        Set the brightness of all LEDs to 0 (off).
        """
        pass

    @overload
    def show(self, image: Image) -> None:
        """
        Display the image.
        """

    @overload
    def show(
        self,
        value: Union[int, float, str, 'Image', List['Image']],
        delay: int = 400,
        *,
        wait: bool = True,
        loop: bool = False,
        clear: bool = False,
    ) -> None:
        """
        If value is a string, float or integer, display letters/digits in sequence. Otherwise, if
        value is an iterable sequence of images, display these images in sequence. Each letter,
        digit or image is shown with delay milliseconds between them.

        If wait is True, this function will block until the animation is finished, otherwise the
        animation will happen in the background.

        If loop is True, the animation will repeat forever.

        If clear is True, the display will be cleared after the iterable has finished.

        Note that the wait, loop and clear arguments must be specified using their keyword.

        Note. If using a generator as the iterable, then take care not to allocate any memory in the
        generator as allocating memory in an interrupt is prohibited and will raise a MemoryError.
        """
        pass

    def scroll(
        self,
        value: str,
        delay: int = 150,
        *,
        wait: bool = True,
        loop: bool = False,
        monospace: bool = False,
    ) -> None:
        """
        Scrolls value horizontally on the display. If value is an integer or float it is first
        converted to a string using str(). The delay parameter controls how fast the text is scrolling.

        If wait is True, this function will block until the animation is finished, otherwise the
        animation will happen in the background.

        If loop is True, the animation will repeat forever.

        If monospace is True, the characters will all take up 5 pixel-columns in width, otherwise
        there will be exactly 1 blank pixel-column between each character as they scroll.

        Note that the wait, loop and monospace arguments must be specified using their keyword.
        """
        pass

    def on(self) -> None:
        """
        Turn on the display.
        """
        pass

    def off(self) -> None:
        """
        Turn off the display (thus allowing you to re-use the GPIO pins associated with the display
        for other purposes).
        """
        pass

    def is_on(self) -> bool:
        """
        Returns True if the display is on, otherwise returns False.
        """
        pass

    def read_light_level(self) -> int:
        """
        Use the display’s LEDs in reverse-bias mode to sense the amount of light falling on the display.
        Returns an integer between 0 and 255 representing the light level, with larger meaning more light.
        """

display : _MicroBitDisplay = ...


# Pins
class _MicroBitDigitalPin(object):
    """
    A standard pin
    """

    PULL_UP: Final[int] = 0
    PULL_DOWN: Final[int] = 1
    NO_PULL: Final[int] = 2


    def read_digital(self) -> int:
        """
        Read the digital value of the pin. 0 for low, 1 for high
        """
        pass

    def write_digital(self, value: int) -> None:
        """
        Set the pin to output high if value is 1, or to low, it it is 0.
        """
        pass

    def set_pull(self, mode: int) -> None:
        """
        Set the pull state to one of three possible values: pin.PULL_UP, pin.PULL_DOWN or pin.NO_PULL
        (where pin is an instance of a pin).
        """

    def get_pull(self) -> int:
        """
        Returns the pull configuration on a pin, which can be one of three possible values: NO_PULL,
        PULL_DOWN, or PULL_UP. These are set using the set_pull() method or automatically configured
        when a pin mode requires it.
        """

    def get_mode(self) -> str:
        """
        Returns the pin mode. When a pin is used for a specific function, like writing a digital
        value, or reading an analog value, the pin mode changes. Pins can have one of the following
        modes: "unused", "analog", "read_digital", "write_digital", "display", "button", "music",
        "audio", "touch", "i2c", "spi".
        """


class _MicroBitAnalogDigitalPin(_MicroBitDigitalPin):
    """
    These pins have ADC & PWM support
    """
    def read_analog(self) -> int:
        """
        Read the voltage applied to the pin.
        Returns the reading as a number between 0 (meaning 0V) and 1023
        (meaning 3.3V).
        """
        pass

    def write_analog(self, value: int) -> None:
        """
        Output a PWM signal on the pin, with the duty cycle proportional to the
        provided value. The value may be either an integer or a floating point number
        between 0 (0% duty cycle) and 1023 (100% duty).
        """
        pass

    def set_analog_period(self, period: int) -> None:
        """
        Set the period of the PWM signal output to period milliseconds.
        The minimum valid value is 1ms.
        """
        pass

    def set_analog_period_microseconds(self, period: int) -> None:
        """
        Set the period of the PWM signal output to period microseconds.
        The minimum valid value is 256µs.
        """
        pass

    def get_analog_period_microseconds(self) -> int:
        ...

class _MicroBitTouchPinBase:
    RESISTIVE: Final[int] = 0
    """Constant for set_touch_mode(...). Available since V2"""
    CAPACITIVE: Final[int] = 1
    """Constant for set_touch_mode(...). Available since V2"""

    def is_touched(self) -> bool:
        """
        Return True if the pin is being touched with a finger, otherwise return False.

        Resistive touch. This test is done by measuring how much resistance there is between the pin
        and ground. A low resistance gives a reading of True. To get a reliable reading using a
        finger you may need to touch the ground pin with another part of your body, for example your
        other hand.

        Capacitive touch. This test is done by interacting with the electric field of a capacitor
        using a finger as a conductor. Capacitive touch does not require you to make a ground
        connection as part of a circuit.
        """
        pass

    def set_touch_mode(self, mode:int) -> None:
        """
        Available since V2. Use pin.CAPACITIVE (no need to touch GND with other hand)
        or pin.RESISTIVE as argument.

        The default for the edge connector pins is resistive and the logo pin in V2 is capacitive.
        """


class _MicroBitTouchPin(_MicroBitTouchPinBase, _MicroBitAnalogDigitalPin):
    """
    These pins are aranged on the bottom of the board and have holes through them
    """

class _MicroBitTouchOnlyPin(_MicroBitTouchPinBase):
    """
    A touch sensitive logo pin on the front of the micro:bit, which by default is set to capacitive touch mode.
    """

pin0 : _MicroBitTouchPin = ...
pin1 : _MicroBitTouchPin = ...
pin2 : _MicroBitTouchPin = ...
pin3 : _MicroBitAnalogDigitalPin = ...
pin4 : _MicroBitAnalogDigitalPin = ...
pin5 : _MicroBitDigitalPin = ...
pin6 : _MicroBitDigitalPin = ...
pin7 : _MicroBitDigitalPin = ...
pin8 : _MicroBitDigitalPin = ...
pin9 : _MicroBitDigitalPin = ...
pin10 : _MicroBitAnalogDigitalPin = ...
pin11 : _MicroBitDigitalPin = ...
pin12 : _MicroBitDigitalPin = ...
pin13 : _MicroBitDigitalPin = ...
pin14 : _MicroBitDigitalPin = ...
pin15 : _MicroBitDigitalPin = ...
pin16 : _MicroBitDigitalPin = ...
# Pin17 : 3v3
# Pin18 : 3v3
pin19 : _MicroBitDigitalPin = ...
pin20 : _MicroBitDigitalPin = ...
# pin21 : gnd
# pin22 : gnd

pin_logo : _MicroBitTouchOnlyPin = ...
"""A touch sensitive logo pin on the front of the micro:bit, which by default is set to capacitive touch mode."""
pin_speaker: _MicroBitDigitalPin = ...
"""A pin to address the micro:bit speaker. This API is intended only for use in Pulse-Width Modulation pin operations eg. pin_speaker.write_analog(128)."""

# I2C
class _MicroBitI2C(object):
    """
    The i2c module lets you communicate with devices connected to your board using the I²C bus protocol.
    There can be multiple slave devices connected at the same time, and each one has its own unique
    address, that is either fixed for the device or configured on it. Your board acts as the I²C master.

    We use 7-bit addressing for devices because of the reasons stated here.

    This may be different to other micro:bit related solutions.

    How exactly you should communicate with the devices, that is, what bytes to send and how to
    interpret the responses, depends on the device in question and should be described separately in
    that device’s documentation.
    """

    def init(self, frequency: int=100000, sda: _MicroBitDigitalPin=pin20,
             scl: _MicroBitDigitalPin=pin19) -> None:
        """
        Re-initialize peripheral with the specified clock frequency freq on the specified sda and scl pins.

        Warning: On a micro:bit V1 board, changing the I²C pins from defaults will make the
        accelerometer and compass stop working, as they are connected internally to those pins. This
        warning does not apply to the V2 revision of the micro:bit as this has separate I²C lines for
        the motion sensors and the edge connector.
        """
        pass

    def scan(self) -> List[int]:
        """
        Scan the bus for devices. Returns a list of 7-bit addresses corresponding to those devices
        that responded to the scan.
        """

    def read(self, addr: int, n: int, repeat: bool = False) -> bytes:
        """
        Read n bytes from the device with 7-bit address addr. If repeat is True, no stop bit will be sent.
        """
        pass

    def write(self, add: int, buffer: bytes, repeat: bool = False) -> None:
        """
        Write bytes from buf to the device with 7-bit address addr. If repeat is True, no stop bit will be sent.
        """
        pass


i2c : _MicroBitI2C = ...


# uart
class _MicroBitUART(object):
    ODD: int = 1
    EVEN: int = 0

    def init(
        self,
        baudrate: int = 9600,
        bits: int = 8,
        parity: Optional[int] = None,
        stop: int = 1,
        *,
        tx: Optional[_MicroBitDigitalPin] = None,
        rx: Optional[_MicroBitDigitalPin] = None,
    ) -> None:
        """
        Initialize serial communication with the specified parameters on the specified tx and rx pins.
        Note that for correct communication, the parameters have to be the same on both communicating devices.

        Warning: Initializing the UART on external pins will cause the Python console on USB to
        become unaccessible, as it uses the same hardware. To bring the console back you must
        reinitialize the UART without passing anything for tx or rx (or passing None to these arguments).
        This means that calling uart.init(115200) is enough to restore the Python console.

        The baudrate defines the speed of communication. Common baud rates include:
        9600, 14400, 19200, 28800, 38400, 57600, 115200.

        The bits defines the size of bytes being transmitted, and the board only supports 8.
        The parity parameter defines how parity is checked, and it can be None, microbit.uart.ODD or
        microbit.uart.EVEN. The stop parameter tells the number of stop bits, and has to be 1 for
        this board.

        If tx and rx are not specified then the internal USB-UART TX/RX pins are used which connect
        to the USB serial converter on the micro:bit, thus connecting the UART to your PC. You can
        specify any other pins you want by passing the desired pin objects to the tx and rx parameters.

        When connecting the device, make sure you “cross” the wires – the TX pin on your board needs
        to be connected with the RX pin on the device, and the RX pin – with the TX pin on the device.
        Also make sure the ground pins of both devices are connected.
        """
        pass

    def any(self) -> bool:
        """
        Return True if any data is waiting, else False.
        """
        pass

    def read(self, nbytes: Optional[int]=...) -> Optional[bytes]:
        """
        Read bytes. If nbytes is specified then read at most that many bytes, otherwise read as many
        bytes as possible.

        Return value: a bytes object or None on timeout.

        A bytes object contains a sequence of bytes. Because ASCII characters can fit in single bytes
        this type of object is often used to represent simple text and offers methods to manipulate
        it as such, e.g. you can display the text using the print() function.

        You can also convert this object into a string object, and if there are non-ASCII characters
        present the encoding can be specified:

            msg_bytes = uart.read()
            msg_str = str(msg, 'UTF-8')

        Note. The timeout for all UART reads depends on the baudrate and is otherwise not changeable
        via Python. The timeout, in milliseconds, is given by: microbit_uart_timeout_char = 13000 /
        baudrate + 1

        Note. The internal UART RX buffer is 64 bytes, so make sure data is read before the buffer
        is full or some of the data might be lost.

        Warning. Receiving 0x03 will stop your program by raising a Keyboard Interrupt. You can enable
        or disable this using micropython.kbd_intr().
        """
        pass


    def readinto(self, buf: bytes, nbytes: Optional[int]=None) -> Optional[int]:
        """
        Read bytes into the buf. If nbytes is specified then read at most that many bytes.
        Otherwise, read at most len(buf) bytes.

        Return value: number of bytes read and stored into buf or None on timeout.
        """
        pass

    def readline(self) -> Optional[bytes]:
        """
        Read a line, ending in a newline character.

        Return value: the line read or None on timeout. The newline character is included in the
        returned bytes.
        """

    def write(self, buf: Union[bytes, str]) -> int:
        """
        Write the buffer to the bus, it can be a bytes object or a string.
        """
        pass


uart : _MicroBitUART = ...


# SPI
class _MicroBitSPI(object):
    def init(
        self,
        baudrate: int = 1000000,
        bits: int = 8,
        mode: int = 0,
        sclk: _MicroBitDigitalPin = pin13,
        mosi: _MicroBitDigitalPin = pin15,
        miso: _MicroBitDigitalPin = pin14,
    ) -> None:
        """
        Initialize SPI communication with the specified parameters on the specified pins. Note that
        for correct communication, the parameters have to be the same on both communicating devices.

        The baudrate defines the speed of communication.

        The bits defines the size of bytes being transmitted. Currently only bits=8 is supported.
        However, this may change in the future.

        The mode determines the combination of clock polarity and phase according to the following
        convention, with polarity as the high order (leftmost) bit and phase as the low order bit:

            * 0 => 00
            * 1 => 01
            * 2 => 10
            * 3 => 11

        Polarity (aka CPOL) 0 means that the clock is at logic value 0 when idle and goes high
        (logic value 1) when active; polarity 1 means the clock is at logic value 1 when idle and
        goes low (logic value 0) when active. Phase (aka CPHA) 0 means that data is sampled on the
        leading edge of the clock, and 1 means on the trailing edge
        (viz. https://en.wikipedia.org/wiki/Signal_edge).

        The sclk, mosi and miso arguments specify the pins to use for each type of signal.
        """
        pass

    def write(self, buf: bytes) -> None:
        """
        Write the buffer of bytes to the bus.
        """
        pass

    def read(self, nbytes: int) -> bytes:
        """
        Read at most nbytes. Returns what was read.
        """
        pass

    def write_readinto(self, outbuf: bytes, inbuf: bytes) -> None:
        """
        Write the out buffer to the bus and read any response into the in buffer. The length of the
        buffers should be the same. The buffers can be the same object.
        """
        pass


spi : _MicroBitSPI = ...

class _MicroBitSpeaker:
    """
    Available since V2.
    """
    def off(self) -> None:
        """
        Turn off the speaker. This does not disable sound output to an edge connector pin.
        """
    def on(self) -> None:
        """
        Turn on the speaker.
        """

speaker: _MicroBitSpeaker = ...


class SoundEvent:
    """
    Enum for describing sound events. Available since V2.
    """
    LOUD: "SoundEvent" = ...
    QUIET: "SoundEvent" = ...

class _MicroBitMicrophone:
    """
    Available since V2.

    This object lets you access the built-in microphone available on the micro:bit V2. It can be used to respond to sound. The microphone input is located on the front of the board alongside a microphone activity LED, which is lit when the microphone is in use.

    The microphone can respond to a pre-defined set of sound events that are based on the amplitude and wavelength of the sound.

    These sound events are represented by instances of the SoundEvent class, accessible via variables in microbit.SoundEvent:

    microbit.SoundEvent.QUIET: Represents the transition of sound events, from loud to quiet like speaking or background music.
    microbit.SoundEvent.LOUD: Represents the transition of sound events, from quiet to loud like clapping or shouting.
    """

    def current_event(self) -> Optional[SoundEvent]:
        """
        return: the name of the last recorded sound event, SoundEvent('loud') or SoundEvent('quiet').
        """

    def was_event(self, event: SoundEvent) -> bool:
        """
        * event: a sound event, such as SoundEvent.LOUD or SoundEvent.QUIET.
        * return: true if sound was heard at least once since the last call, otherwise false. was_event() also clears the sound event history before returning.
        """
    def is_event(self, event: SoundEvent) -> bool:
        """
        * event: a sound event, such as SoundEvent.LOUD or SoundEvent.QUIET.
        * return: true if sound event is the most recent since the last call, otherwise false. It does not clear the sound event history.
        """

    def get_events(self) -> Tuple[SoundEvent]:
        """
        Return a tuple of the event history. The most recent is listed last. get_events() also clears the sound event history before returning.
        """

    def set_threshold(self, event: SoundEvent, value: int) -> None:
        """
        * event: a sound event, such as SoundEvent.LOUD or SoundEvent.QUIET.
        * value: The threshold level in the range 0-255. For example, set_threshold(SoundEvent.LOUD, 250) will only trigger if the sound is very loud (>= 250).
        """

    def sound_level(self) -> int:
        """
        Return a representation of the sound pressure level in the range 0 to 255.
        """

def set_volume(value: int) -> None:
    """
    sets the output volume (0-255) of the micro:bit speaker (V2) and
    external speaker or headphones connected to the edge connector pins.
    """

def ws2812_write(pin, buffer) -> None:
    ...

class Sound:
    """Enum for sound constants. Since V2. Can be used in audio.play"""

    GIGGLE: "Sound" = ...
    HAPPY: "Sound" = ...
    HELLO: "Sound" = ...
    MYSTERIOUS: "Sound" = ...
    SAD: "Sound" = ...
    SLIDE: "Sound" = ...
    SOARING: "Sound" = ...
    SPRING: "Sound" = ...
    TWINKLE: "Sound" = ...
    YAWN: "Sound" = ...
