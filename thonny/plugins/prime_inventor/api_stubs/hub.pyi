"""
The lower-level hub API.

Described at https://lego.github.io/MINDSTORMS-Robot-Inventor-hub-API/
"""
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
    overload,
)

__version__: str
"""
The firmware version of the form 'v1.0.06.0034-b0c335b', consisting of the components:
v major . minor . bugfix . build - hash.
"""

config: Dict[str, Any] = {}

# Orientation constants
TOP: Final[int] = 0
FRONT: Final[int] = 1
RIGHT: Final[int] = 2
BOTTOM: Final[int] = 3
BACK: Final[int] = 4
LEFT: Final[int] = 5

class _Button(Protocol):
    """
    Provides access to button state and callback.

    Each of the buttons listed in `hub.button` are instances of this class. You cannot instantiate additional button objects.
    """

    def is_pressed(self) -> bool:
        """
        Gets the state of the button.
        """
    def was_pressed(self) -> bool:
        """
        Checks if this button was pressed since this method was last called.
        """
    def presses(self) -> int:
        """
        Gets the number of times this button was pressed since this method was last called.
        """
    def on_change(self, function: Optional[Callable[[int], None]]) -> Any:
        """TODO: Same as `callback`?"""
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """
        Sets the callback function that is called when the button is pressed and when it is released.
        Choose None to disable the callback.

        The function must accept one argument, whose value indicates why the callback was called.
        If the value is 0, the button is now pressed.
        Otherwise, the button is now released. The value represents how many milliseconds it was pressed before it was released.
        """

class _Device(Protocol):
    """
    Read values from a Powered Up device and configure its modes.

    This class is the blueprint for the device attributes of the ports in the ``hub.port`` module, which in turn are instances of the Port class. You cannot import or instantiate this class manually.
    """

    # TODO:

class _Motor(Protocol):
    """
    TODO:
    """

class _MotorPair(Protocol):
    """
    TODO:
    """

class _Pin(Protocol):
    def direction(self, direction: Optional[int]) -> int:
        """"""
    def value(self, value: Optional[int]) -> int:
        """"""

class _Port(Protocol):
    """
    Provides access to port configuration and devices on a port. Some methods and attributes can only be used if the port is in the right mode, as shown below.

    This class is the blueprint for the port instances in the ``hub.port`` module. Those instances are automatically instantiated on boot, and further populated when devices are plugged in. You cannot import or instantiate this class manually.
    """

    device: Optional[_Device]
    motor: Optional[_Motor]
    p5: _Pin
    p6: _Pin

    def pwm(self, value: int) -> None:
        """"""
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """"""
    def mode(self, mode: int, baud_rate: int = 2400) -> None:
        """"""
    def info(self) -> Dict[str, Any]:
        """"""
    def baud(self, baud: int) -> None:
        """"""
    def read(self, read: Union[int, Any]) -> int:
        """"""
    def write(self, data: bytes) -> int:
        """"""

class _battery(Protocol):
    """
    Battery-related constants and functions.
    """

    BATTERY_BAD_BATTERY: Final[int] = -4
    BATTERY_HUB_TEMPERATURE_CRITICAL_OUT_OF_RANGE: Final[int] = -2
    BATTERY_MISSING: Final[int] = -6
    BATTERY_NO_ERROR: Final[int] = 0
    BATTERY_TEMPERATURE_OUT_OF_RANGE: Final[int] = -2
    BATTERY_TEMPERATURE_SENSOR_FAIL: Final[int] = -3
    BATTERY_VOLTAGE_TOO_LOW: Final[int] = -5
    CHARGER_STATE_CHARGING_COMPLETED: Final[int] = 2
    CHARGER_STATE_CHARGING_ONGOING: Final[int] = 1
    CHARGER_STATE_DISCHARGING: Final[int] = 0
    CHARGER_STATE_FAIL: Final[int] = -1
    USB_CH_PORT_CDP: Final[int] = 2
    USB_CH_PORT_DCP: Final[int] = 3
    USB_CH_PORT_NONE: Final[int] = 0
    USB_CH_PORT_SDP: Final[int] = 1

    def voltage(self) -> int:
        """"""
    def current(self) -> int:
        """"""
    def capacity_left(self) -> int:
        """"""
    def temperature(self) -> float:
        """"""
    def info(self) -> Dict[str, Any]:
        """"""
    def charger_detect(self) -> Union[bool, int]:
        """"""

class _bluetooth(Protocol):
    @overload
    def discoverable(self) -> int:
        """"""
    @overload
    def discoverable(self, time: int) -> None:
        """"""
    @overload
    def rfcomm_connect(self) -> str:
        """"""
    @overload
    def rfcomm_connect(self, address: str) -> None:
        """"""
    def rfcomm_disconnect(self) -> None:
        """"""
    def info(self) -> Dict[str, Any]:
        """"""
    def forget(self, address: str) -> bool:
        """"""
    @overload
    def lwp_advertise(self) -> int:
        """"""
    @overload
    def lwp_advertise(self, bypass: bool) -> None:
        """"""
    @overload
    def lwp_bypass(self) -> bool:
        """"""
    @overload
    def lwp_bypass(self, bypass: bool) -> None:
        """"""
    def lwp_monitor(self, handler: Optional[Callable[[int], None]]) -> None:
        """"""

class _button(Protocol):
    """
    Button instances.
    """

    center: _Button
    connect: _Button
    left: _Button
    right: _Button

class _display(Protocol):
    def clear(self) -> None:
        """"""
    def rotation(self, rotation: int) -> None:
        """"""
    @overload
    def align(self) -> int:
        """"""
    @overload
    def align(self, face: int) -> int:
        """"""
    @overload
    def invert(self) -> bool:
        """"""
    @overload
    def invert(self, invert: bool) -> bool:
        """"""
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """"""
    @overload
    def pixel(self, x: int, y: int) -> int:
        """"""
    @overload
    def pixel(self, x: int, y: int, brightness: int) -> None:
        """"""
    @overload
    def show(self, image: Image) -> None:
        """"""
    @overload
    def show(
        self,
        image: Iterable[Image],
        delay: int = 400,
        level: int = 9,
        clear: bool = False,
        wait: bool = True,
        loop: bool = False,
        fade: int = 0,
    ) -> None:
        """"""

class _motion(Protocol):
    DOUBLETAPPED: Final[int] = 1
    FREEFALL: Final[int] = 3
    SHAKE: Final[int] = 2
    TAPPED: Final[int] = 0

    def accelerometer(self, filtered: bool = False) -> Tuple[int, int, int]:
        """"""
    def gyroscope(self, filtered: bool = False) -> Tuple[int, int, int]:
        """"""
    @overload
    def align_to_model(self, top: int, front: int) -> None:
        """"""
    @overload
    def align_to_model(self, nsamples: int, callback: Callable[[int], None]) -> None:
        """"""
    @overload
    def align_to_model(
        self, top: int, front: int, nsamples: int, callback: Callable[[int], None]
    ) -> None:
        """"""
    @overload
    def yaw_pitch_roll(self) -> Tuple[int, int, int]:
        """"""
    @overload
    def yaw_pitch_roll(self, yaw_preset: int) -> None:
        """"""
    @overload
    def yaw_pitch_roll(self, yaw_correction: float) -> None:
        """"""
    @overload
    def orientation(self) -> int:
        """"""
    @overload
    def orientation(self, callback: Optional[Callable[[int], None]]) -> int:
        """"""
    @overload
    def gesture(self) -> int:
        """"""
    @overload
    def gesture(self, callback: Optional[Callable[[int], None]]) -> int:
        """"""

class _port(Protocol):
    A: _Port
    B: _Port
    C: _Port
    D: _Port
    E: _Port
    F: _Port

    DETACHED: Final[int] = 0
    ATTACHED: Final[int] = 1

    MODE_DEFAULT: Final[int] = 0
    MODE_FULL_DUPLEX: Final[int] = 1
    MODE_HALF_DUPLEX: Final[int] = 2
    MODE_GPIO: Final[int] = 3

class _sound(Protocol):
    SOUND_SIN: Final[int] = 0
    SOUND_SQUARE: Final[int] = 1
    SOUND_TRIANGLE: Final[int] = 2
    SOUND_SAWTOOTH: Final[int] = 3

    @overload
    def volume(self, volume: int) -> None:
        """"""
    @overload
    def volume(self) -> int:
        """"""
    def beep(self, freq: int = 1000, time: int = 1000, waveform: int = 0) -> None:
        """"""
    def play(self, filename: str, rate: int = 16000) -> None:
        """"""
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """"""

class _supervision(Protocol):
    def info(self) -> Dict[str, Any]:
        """"""
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """"""

class Image:
    ALL_ARROWS: Tuple[Image, Image, Image, Image, Image, Image, Image, Image]
    ALL_CLOCKS: Tuple[
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
        Image,
    ]
    ANGRY: Image  ## <class 'Image'> = Image('90009:09090:00000:99999:90909:')
    ARROW_E: Image  ## <class 'Image'> = Image('00900:00090:99999:00090:00900:')
    ARROW_N: Image  ## <class 'Image'> = Image('00900:09990:90909:00900:00900:')
    ARROW_NE: Image  ## <class 'Image'> = Image('00999:00099:00909:09000:90000:')
    ARROW_NW: Image  ## <class 'Image'> = Image('99900:99000:90900:00090:00009:')
    ARROW_S: Image  ## <class 'Image'> = Image('00900:00900:90909:09990:00900:')
    ARROW_SE: Image  ## <class 'Image'> = Image('90000:09000:00909:00099:00999:')
    ARROW_SW: Image  ## <class 'Image'> = Image('00009:00090:90900:99000:99900:')
    ARROW_W: Image  ## <class 'Image'> = Image('00900:09000:99999:09000:00900:')
    ASLEEP: Image  ## <class 'Image'> = Image('00000:99099:00000:09990:00000:')
    BUTTERFLY: Image  ## <class 'Image'> = Image('99099:99999:00900:99999:99099:')
    CHESSBOARD: Image  ## <class 'Image'> = Image('09090:90909:09090:90909:09090:')
    CLOCK1: Image  ## <class 'Image'> = Image('00090:00090:00900:00000:00000:')
    CLOCK10: Image  ## <class 'Image'> = Image('00000:99000:00900:00000:00000:')
    CLOCK11: Image  ## <class 'Image'> = Image('09000:09000:00900:00000:00000:')
    CLOCK12: Image  ## <class 'Image'> = Image('00900:00900:00900:00000:00000:')
    CLOCK2: Image  ## <class 'Image'> = Image('00000:00099:00900:00000:00000:')
    CLOCK3: Image  ## <class 'Image'> = Image('00000:00000:00999:00000:00000:')
    CLOCK4: Image  ## <class 'Image'> = Image('00000:00000:00900:00099:00000:')
    CLOCK5: Image  ## <class 'Image'> = Image('00000:00000:00900:00090:00090:')
    CLOCK6: Image  ## <class 'Image'> = Image('00000:00000:00900:00900:00900:')
    CLOCK7: Image  ## <class 'Image'> = Image('00000:00000:00900:09000:09000:')
    CLOCK8: Image  ## <class 'Image'> = Image('00000:00000:00900:99000:00000:')
    CLOCK9: Image  ## <class 'Image'> = Image('00000:00000:99900:00000:00000:')
    CONFUSED: Image  ## <class 'Image'> = Image('00000:09090:00000:09090:90909:')
    COW: Image  ## <class 'Image'> = Image('90009:90009:99999:09990:00900:')
    DIAMOND: Image  ## <class 'Image'> = Image('00900:09090:90009:09090:00900:')
    DIAMOND_SMALL: Image  ## <class 'Image'> = Image('00000:00900:09090:00900:00000:')
    DUCK: Image  ## <class 'Image'> = Image('09900:99900:09999:09990:00000:')
    FABULOUS: Image  ## <class 'Image'> = Image('99999:99099:00000:09090:09990:')
    GHOST: Image  ## <class 'Image'> = Image('99999:90909:99999:99999:90909:')
    GIRAFFE: Image  ## <class 'Image'> = Image('99000:09000:09000:09990:09090:')
    GO_DOWN: Image  ## <class 'Image'> = Image('00000:99999:09990:00900:00000:')
    GO_LEFT: Image  ## <class 'Image'> = Image('00090:00990:09990:00990:00090:')
    GO_RIGHT: Image  ## <class 'Image'> = Image('09000:09900:09990:09900:09000:')
    GO_UP: Image  ## <class 'Image'> = Image('00000:00900:09990:99999:00000:')
    HAPPY: Image  ## <class 'Image'> = Image('00000:09090:00000:90009:09990:')
    HEART: Image  ## <class 'Image'> = Image('09090:99999:99999:09990:00900:')
    HEART_SMALL: Image  ## <class 'Image'> = Image('00000:09090:09990:00900:00000:')
    HOUSE: Image  ## <class 'Image'> = Image('00900:09990:99999:09990:09090:')
    MEH: Image  ## <class 'Image'> = Image('09090:00000:00090:00900:09000:')
    MUSIC_CROTCHET: Image  ## <class 'Image'> = Image('00900:00900:00900:99900:99900:')
    MUSIC_QUAVER: Image  ## <class 'Image'> = Image('00900:00990:00909:99900:99900:')
    MUSIC_QUAVERS: Image  ## <class 'Image'> = Image('09999:09009:09009:99099:99099:')
    NO: Image  ## <class 'Image'> = Image('90009:09090:00900:09090:90009:')
    PACMAN: Image  ## <class 'Image'> = Image('09999:99090:99900:99990:09999:')
    PITCHFORK: Image  ## <class 'Image'> = Image('90909:90909:99999:00900:00900:')
    RABBIT: Image  ## <class 'Image'> = Image('90900:90900:99990:99090:99990:')
    ROLLERSKATE: Image  ## <class 'Image'> = Image('00099:00099:99999:99999:09090:')
    SAD: Image  ## <class 'Image'> = Image('00000:09090:00000:09990:90009:')
    SILLY: Image  ## <class 'Image'> = Image('90009:00000:99999:00909:00999:')
    SKULL: Image  ## <class 'Image'> = Image('09990:90909:99999:09990:09990:')
    SMILE: Image  ## <class 'Image'> = Image('00000:00000:00000:90009:09990:')
    SNAKE: Image  ## <class 'Image'> = Image('99000:99099:09090:09990:00000:')
    SQUARE: Image  ## <class 'Image'> = Image('99999:90009:90009:90009:99999:')
    SQUARE_SMALL: Image  ## <class 'Image'> = Image('00000:09990:09090:09990:00000:')
    STICKFIGURE: Image  ## <class 'Image'> = Image('00900:99999:00900:09090:90009:')
    SURPRISED: Image  ## <class 'Image'> = Image('09090:00000:00900:09090:00900:')
    SWORD: Image  ## <class 'Image'> = Image('00900:00900:00900:09990:00900:')
    TARGET: Image  ## <class 'Image'> = Image('00900:09990:99099:09990:00900:')
    TORTOISE: Image  ## <class 'Image'> = Image('00000:09990:99999:09090:00000:')
    TRIANGLE: Image  ## <class 'Image'> = Image('00000:00900:09090:99999:00000:')
    TRIANGLE_LEFT: Image  ## <class 'Image'> = Image('90000:99000:90900:90090:99999:')
    TSHIRT: Image  ## <class 'Image'> = Image('99099:99999:09990:09990:09990:')
    UMBRELLA: Image  ## <class 'Image'> = Image('09990:99999:00900:90900:09900:')
    XMAS: Image  ## <class 'Image'> = Image('00900:09990:00900:09990:99999:')
    YES: Image  ## <class 'Image'> = Image('00000:00009:00090:90900:09000:')

    @overload
    def __init__(self, string: str) -> None:
        """"""
    @overload
    def __init__(self, width: int, height: int) -> None:
        """"""
    @overload
    def __init__(self, width: int, height: int, buffer: bytes) -> None:
        """"""
    def width(self) -> int:
        """"""
    def height(self) -> int:
        """"""
    def shift_left(self, n: int) -> Image:
        """"""
    def shift_right(self, n: int) -> Image:
        """"""
    def shift_up(self, n: int) -> Image:
        """"""
    def shift_down(self, n: int) -> Image:
        """"""
    def get_pixel(self, x: int, y: int) -> int:
        """"""
    def set_pixel(self, x: int, y: int, brightness: int) -> None:
        """"""

class BT_VCP:
    def __init__(self, id: int = 0) -> None:
        """"""
    def setinterrupt(self, chr: int) -> None:
        """"""
    def isconnected(self) -> bool:
        """"""
    def any(self) -> bool:
        """"""
    def close(self) -> None:
        """"""
    @overload
    def read(self) -> Optional[bytes]:
        """"""
    @overload
    def read(self, nbytes: int) -> Optional[bytes]:
        """"""
    @overload
    def readinto(self, buf) -> Optional[int]:
        """"""
    @overload
    def readinto(self, buf: bytearray, maxlen: int) -> Optional[int]:
        """"""
    def readline(self) -> Optional[bytes]:
        """"""
    def readlines(self, *args, **kwargs) -> List[bytes]:
        """"""
    def write(self, buf: bytes) -> int:
        """"""
    def recv(self, data: Union[int, bytearray], timeout: int = 5000) -> int:
        """"""
    def send(self, data: Union[int, bytes], timeout: int = 5000) -> int:
        """"""
    @overload
    def callback(self) -> Optional[Callable[[int], None]]:
        """"""
    @overload
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """"""

class USB_VCP:
    RTS: Final[int] = 1
    CTS: Final[int] = 2

    def __init__(self, id: int = 0) -> None:
        """"""
    def init(self, flow: int = -1) -> None:
        """"""
    def setinterrupt(self, chr: int) -> None:
        """"""
    def isconnected(self) -> bool:
        """"""
    def any(self) -> bool:
        """"""
    def close(self) -> None:
        """"""
    @overload
    def read(self) -> Optional[bytes]:
        """"""
    @overload
    def read(self, nbytes: int) -> Optional[bytes]:
        """"""
    @overload
    def readinto(self, buf) -> Optional[int]:
        """"""
    @overload
    def readinto(self, buf: bytearray, maxlen: int) -> Optional[int]:
        """"""
    def readline(self) -> Optional[bytes]:
        """"""
    def readlines(self, *args, **kwargs) -> List[bytes]:
        """"""
    def write(self, buf: bytes) -> int:
        """"""
    def recv(self, data: Union[int, bytearray], timeout: int = 5000) -> int:
        """"""
    def send(self, data: Union[int, bytes], timeout: int = 5000) -> int:
        """"""
    @overload
    def callback(self) -> Optional[Callable[[int], None]]:
        """"""
    @overload
    def callback(self, function: Optional[Callable[[int], None]]) -> None:
        """"""

battery: _battery

bluetooth: _bluetooth

button: _button

display: _display

motion: _motion

port: _port

sound: _sound

supervision: _supervision

def info() -> Dict[str, Any]:
    """Returns information about the hub"""

def status() -> Dict[str, Any]:
    """Returns status of the components."""

@overload
def power_off(fast: bool = True, restart: bool = False) -> None:
    """
    Turns the hub off.

    Use fast=True for fast shut down, without the usual light animation and sound.
    Use restart=True to reboot after shutting down.
    """

@overload
def power_off(timeout: int = 0) -> None:
    """Sets the inactivity timeout before the hub shuts down automatically."""

def repl_restart(restart: bool = True) -> None:
    """
    Resets the REPL and clears all variables if restart=True.

    Does nothing if restart=False.
    """

def temperature() -> float:
    """Returns hub's temperature in Celsius degrees."""

@overload
def led(color: int, /) -> None:
    """Sets the color of the LED in the center button of the hub.

    0 = off
    1 = pink
    2 = violet
    3 = blue
    4 = turquoise
    5 = light green
    6 = green
    7 = yellow
    8 = orange
    9 = red
    10 = white
    """

@overload
def led(red: int, green: int, blue: int, /) -> None:
    """Sets the color of the LED in the center button of the hub as RGB components (0-255)."""

@overload
def led(color: Tuple[int, int, int], /) -> None:
    """Sets the color of the LED in the center button of the hub as tuple of RGB components (0-255)."""

def file_transfer(
    filename: str,
    filesize: int,
    packetsize: int = 1000,
    timeout: int = 2000,
    mode: Optional[str] = None,
) -> None:
    """Prepares a file transfer to the hub."""

def reset() -> None:
    """Resets the hub."""
