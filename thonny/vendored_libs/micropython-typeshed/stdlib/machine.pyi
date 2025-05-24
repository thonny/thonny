"""
Functions related to the hardware.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/machine.html

The ``machine`` module contains specific functions related to the hardware
on a particular board. Most functions in this module allow to achieve direct
and unrestricted access to and control of hardware blocks on a system
(like CPU, timers, buses, etc.). Used incorrectly, this can lead to
malfunction, lockups, crashes of your board, and in extreme cases, hardware
damage.

---
Module: 'machine' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import NoReturn, Optional, Union, Tuple, Any, Callable, List, Sequence, overload, Final
from _typeshed import Incomplete
from typing_extensions import deprecated, Awaitable, TypeAlias, TypeVar
from _mpy_shed import _IRQ, AnyReadableBuf, AnyWritableBuf
from vfs import AbstractBlockDev

ULP_WAKE: Final[int] = 6
SLEEP: Final[int] = 2
PWRON_RESET: Final[int] = 1
PIN_WAKE: Final[int] = 2
SOFT_RESET: Final[int] = 5
WDT_RESET: Final[int] = 3
TOUCHPAD_WAKE: Final[int] = 5
TIMER_WAKE: Final[int] = 4
HARD_RESET: Final[int] = 2
EXT0_WAKE: Final[int] = 2
DEEPSLEEP_RESET: Final[int] = 4
DEEPSLEEP: Final[int] = 4
EXT1_WAKE: Final[int] = 3
ATTN_0DB: int = ...
ID_T: TypeAlias = int | str
PinLike: TypeAlias = Pin | int | str
IDLE: Incomplete
WLAN_WAKE: Incomplete
RTC_WAKE: Incomplete

@overload
def deepsleep() -> NoReturn:
    """
    Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A lightsleep has full RAM and state retention.  Upon wake execution is resumed
      from the point where the sleep was requested, with all subsystems operational.

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
      from other resets.
    """

@overload
def deepsleep(time_ms: int, /) -> NoReturn:
    """
    Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A lightsleep has full RAM and state retention.  Upon wake execution is resumed
      from the point where the sleep was requested, with all subsystems operational.

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
      from other resets.
    """

def soft_reset() -> NoReturn:
    """
    Performs a :ref:`soft reset <soft_reset>` of the interpreter, deleting all
    Python objects and resetting the Python heap.
    """
    ...

def dht_readinto(*args, **kwargs) -> Incomplete: ...
def reset() -> NoReturn:
    """
    :ref:`Hard resets <hard_reset>` the device in a manner similar to pushing the
    external RESET button.
    """
    ...

def unique_id() -> bytes:
    """
    Returns a byte string with a unique identifier of a board/SoC. It will vary
    from a board/SoC instance to another, if underlying hardware allows. Length
    varies by hardware (so use substring of a full value if you expect a short
    ID). In some MicroPython ports, ID corresponds to the network MAC address.
    """
    ...

def time_pulse_us(pin: Pin, pulse_level: int, timeout_us: int = 1_000_000, /) -> int:
    """
    Time a pulse on the given *pin*, and return the duration of the pulse in
    microseconds.  The *pulse_level* argument should be 0 to time a low pulse
    or 1 to time a high pulse.

    If the current input value of the pin is different to *pulse_level*,
    the function first (*) waits until the pin input becomes equal to *pulse_level*,
    then (**) times the duration that the pin is equal to *pulse_level*.
    If the pin is already equal to *pulse_level* then timing starts straight away.

    The function will return -2 if there was timeout waiting for condition marked
    (*) above, and -1 if there was timeout during the main measurement, marked (**)
    above. The timeout is the same for both cases and given by *timeout_us* (which
    is in microseconds).
    """
    ...

def bitstream(pin, encoding, timing, data, /) -> Incomplete:
    """
    Transmits *data* by bit-banging the specified *pin*. The *encoding* argument
    specifies how the bits are encoded, and *timing* is an encoding-specific timing
    specification.

    The supported encodings are:

      - ``0`` for "high low" pulse duration modulation. This will transmit 0 and
        1 bits as timed pulses, starting with the most significant bit.
        The *timing* must be a four-tuple of nanoseconds in the format
        ``(high_time_0, low_time_0, high_time_1, low_time_1)``. For example,
        ``(400, 850, 800, 450)`` is the timing specification for WS2812 RGB LEDs
        at 800kHz.

    The accuracy of the timing varies between ports. On Cortex M0 at 48MHz, it is
    at best +/- 120ns, however on faster MCUs (ESP8266, ESP32, STM32, Pyboard), it
    will be closer to +/-30ns.

    ``Note:`` For controlling WS2812 / NeoPixel strips, see the :mod:`neopixel`
       module for a higher-level API.
    """
    ...

def idle() -> None:
    """
    Gates the clock to the CPU, useful to reduce power consumption at any time
    during short or long periods. Peripherals continue working and execution
    resumes as soon as any interrupt is triggered, or at most one millisecond
    after the CPU was paused.

    It is recommended to call this function inside any tight loop that is
    continuously checking for an external change (i.e. polling). This will reduce
    power consumption without significantly impacting performance. To reduce
    power consumption further then see the :func:`lightsleep`,
    :func:`time.sleep()` and :func:`time.sleep_ms()` functions.
    """
    ...

@overload
def freq() -> int:
    """
    Returns the CPU frequency in hertz.

    On some ports this can also be used to set the CPU frequency by passing in *hz*.
    """

@overload
def freq(hz: int, /) -> None:
    """
    Returns the CPU frequency in hertz.

    On some ports this can also be used to set the CPU frequency by passing in *hz*.
    """

@overload
def freq(self) -> int:
    """
    Returns the CPU frequency in hertz.

    On some ports this can also be used to set the CPU frequency by passing in *hz*.
    """

@overload
def freq(
    self,
    value: int,
    /,
) -> None:
    """
    Returns the CPU frequency in hertz.

    On some ports this can also be used to set the CPU frequency by passing in *hz*.
    """

@overload
def lightsleep() -> None:
    """
    Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A lightsleep has full RAM and state retention.  Upon wake execution is resumed
      from the point where the sleep was requested, with all subsystems operational.

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
      from other resets.
    """

@overload
def lightsleep(time_ms: int, /) -> None:
    """
    Stops execution in an attempt to enter a low power state.

    If *time_ms* is specified then this will be the maximum time in milliseconds that
    the sleep will last for.  Otherwise the sleep can last indefinitely.

    With or without a timeout, execution may resume at any time if there are events
    that require processing.  Such events, or wake sources, should be configured before
    sleeping, like `Pin` change or `RTC` timeout.

    The precise behaviour and power-saving capabilities of lightsleep and deepsleep is
    highly dependent on the underlying hardware, but the general properties are:

    * A lightsleep has full RAM and state retention.  Upon wake execution is resumed
      from the point where the sleep was requested, with all subsystems operational.

    * A deepsleep may not retain RAM or any other state of the system (for example
      peripherals or network interfaces).  Upon wake execution is resumed from the main
      script, similar to a hard or power-on reset. The `reset_cause()` function will
      return `machine.DEEPSLEEP` and this can be used to distinguish a deepsleep wake
      from other resets.
    """

def disable_irq() -> bool:
    """
    Disable interrupt requests.
    Returns the previous IRQ state which should be considered an opaque value.
    This return value should be passed to the `enable_irq()` function to restore
    interrupts to their original state, before `disable_irq()` was called.
    """
    ...

def enable_irq(state: bool = True, /) -> None:
    """
    Re-enable interrupt requests.
    The *state* parameter should be the value that was returned from the most
    recent call to the `disable_irq()` function.
    """
    ...

def reset_cause() -> int:
    """
    Get the reset cause. See :ref:`constants <machine_constants>` for the possible return values.
    """
    ...

@deprecated("use :func:`lightsleep()` instead.")
def sleep() -> None:
    """
    ``Note:`` This function is deprecated, use :func:`lightsleep()` instead with no arguments.
    """
    ...

def wake_reason() -> int:
    """
    Get the wake reason. See :ref:`constants <machine_constants>` for the possible return values.

    Availability: ESP32, WiPy.
    """
    ...

mem8: Incomplete  ## <class 'mem'> = <8-bit memory>

class PWM:
    """
    This class provides pulse width modulation output.

    Example usage::

        from machine import PWM

        pwm = PWM(pin)          # create a PWM object on a pin
        pwm.duty_u16(32768)     # set duty to 50%

        # reinitialise with a period of 200us, duty of 5us
        pwm.init(freq=5000, duty_ns=5000)

        pwm.duty_ns(3000)       # set pulse width to 3us

        pwm.deinit()


    Limitations of PWM
    ------------------

    * Not all frequencies can be generated with absolute accuracy due to
      the discrete nature of the computing hardware.  Typically the PWM frequency
      is obtained by dividing some integer base frequency by an integer divider.
      For example, if the base frequency is 80MHz and the required PWM frequency is
      300kHz the divider must be a non-integer number 80000000 / 300000 = 266.67.
      After rounding the divider is set to 267 and the PWM frequency will be
      80000000 / 267 = 299625.5 Hz, not 300kHz.  If the divider is set to 266 then
      the PWM frequency will be 80000000 / 266 = 300751.9 Hz, but again not 300kHz.

    * The duty cycle has the same discrete nature and its absolute accuracy is not
      achievable.  On most hardware platforms the duty will be applied at the next
      frequency period.  Therefore, you should wait more than "1/frequency" before
      measuring the duty.

    * The frequency and the duty cycle resolution are usually interdependent.
      The higher the PWM frequency the lower the duty resolution which is available,
      and vice versa. For example, a 300kHz PWM frequency can have a duty cycle
      resolution of 8 bit, not 16-bit as may be expected.  In this case, the lowest
      8 bits of *duty_u16* are insignificant. So::

        pwm=PWM(Pin(13), freq=300_000, duty_u16=2**16//2)

      and::

        pwm=PWM(Pin(13), freq=300_000, duty_u16=2**16//2 + 255)

      will generate PWM with the same 50% duty cycle.
    """

    @overload
    def duty_u16(self) -> int:
        """
        Get or set the current duty cycle of the PWM output, as an unsigned 16-bit
        value in the range 0 to 65535 inclusive.

        With no arguments the duty cycle is returned.

        With a single *value* argument the duty cycle is set to that value, measured
        as the ratio ``value / 65535``.
        """

    @overload
    def duty_u16(
        self,
        value: int,
        /,
    ) -> None:
        """
        Get or set the current duty cycle of the PWM output, as an unsigned 16-bit
        value in the range 0 to 65535 inclusive.

        With no arguments the duty cycle is returned.

        With a single *value* argument the duty cycle is set to that value, measured
        as the ratio ``value / 65535``.
        """

    def init(self, *, freq: int = ..., duty_u16: int = ..., duty_ns: int = ...) -> None:
        """
        Modify settings for the PWM object.  See the above constructor for details
        about the parameters.
        """
        ...

    @overload
    def freq(self) -> int:
        """
        Get or set the current frequency of the PWM output.

        With no arguments the frequency in Hz is returned.

        With a single *value* argument the frequency is set to that value in Hz.  The
        method may raise a ``ValueError`` if the frequency is outside the valid range.
        """

    @overload
    def freq(
        self,
        value: int,
        /,
    ) -> None:
        """
        Get or set the current frequency of the PWM output.

        With no arguments the frequency in Hz is returned.

        With a single *value* argument the frequency is set to that value in Hz.  The
        method may raise a ``ValueError`` if the frequency is outside the valid range.
        """

    def deinit(self) -> None:
        """
        Disable the PWM output.
        """
        ...

    @overload
    def duty_ns(self) -> int:
        """
        Get or set the current pulse width of the PWM output, as a value in nanoseconds.

        With no arguments the pulse width in nanoseconds is returned.

        With a single *value* argument the pulse width is set to that value.
        """

    @overload
    def duty_ns(
        self,
        value: int,
        /,
    ) -> None:
        """
        Get or set the current pulse width of the PWM output, as a value in nanoseconds.

        With no arguments the pulse width in nanoseconds is returned.

        With a single *value* argument the pulse width is set to that value.
        """

    def duty(self, *args, **kwargs) -> Incomplete: ...
    def __init__(
        self,
        dest: PinLike,
        /,
        *,
        freq: int = ...,
        duty_u16: int = ...,
        duty_ns: int = ...,
    ) -> None:
        """
        Construct and return a new PWM object using the following parameters:

           - *dest* is the entity on which the PWM is output, which is usually a
             :ref:`machine.Pin <machine.Pin>` object, but a port may allow other values,
             like integers.
           - *freq* should be an integer which sets the frequency in Hz for the
             PWM cycle.
           - *duty_u16* sets the duty cycle as a ratio ``duty_u16 / 65535``.
           - *duty_ns* sets the pulse width in nanoseconds.

        Setting *freq* may affect other PWM objects if the objects share the same
        underlying PWM generator (this is hardware specific).
        Only one of *duty_u16* and *duty_ns* should be specified at a time.
        """

class UART:
    """
    UART implements the standard UART/USART duplex serial communications protocol.  At
    the physical level it consists of 2 lines: RX and TX.  The unit of communication
    is a character (not to be confused with a string character) which can be 8 or 9
    bits wide.

    UART objects can be created and initialised using::

        from machine import UART

        uart = UART(1, 9600)                         # init with given baudrate
        uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

    Supported parameters differ on a board:

    Pyboard: Bits can be 7, 8 or 9. Stop can be 1 or 2. With *parity=None*,
    only 8 and 9 bits are supported.  With parity enabled, only 7 and 8 bits
    are supported.

    WiPy/CC3200: Bits can be 5, 6, 7, 8. Stop can be 1 or 2.

    A UART object acts like a `stream` object and reading and writing is done
    using the standard stream methods::

        uart.read(10)       # read 10 characters, returns a bytes object
        uart.read()         # read all available characters
        uart.readline()     # read a line
        uart.readinto(buf)  # read and store into the given buffer
        uart.write('abc')   # write the 3 characters
    """

    INV_RX: Final[int] = 4
    INV_TX: Final[int] = 32
    INV_RTS: Final[int] = 64
    RTS: Final[int] = 1
    IRQ_RXIDLE: Final[int] = 4096
    IRQ_BREAK: Final[int] = 2
    IRQ_RX: Final[int] = 1
    INV_CTS: Final[int] = 8
    CTS: Final[int] = 2
    IRQ_TXIDLE: Incomplete
    IDLE: int = ...
    def irq(
        self,
        handler: Callable[[UART], None] | None = None,
        trigger: int = 0,
        hard: bool = False,
        /,
    ) -> _IRQ:
        """
        Configure an interrupt handler to be called when a UART event occurs.

        The arguments are:

          - *handler* is an optional function to be called when the interrupt event
            triggers.  The handler must take exactly one argument which is the
            ``UART`` instance.

          - *trigger* configures the event(s) which can generate an interrupt.
            Possible values are a mask of one or more of the following:

            - ``UART.IRQ_RXIDLE`` interrupt after receiving at least one character
              and then the RX line goes idle.
            - ``UART.IRQ_RX`` interrupt after each received character.
            - ``UART.IRQ_TXIDLE`` interrupt after or while the last character(s) of
              a message are or have been sent.
            - ``UART.IRQ_BREAK`` interrupt when a break state is detected at RX

          - *hard* if true a hardware interrupt is used.  This reduces the delay
            between the pin change and the handler being called. Hard interrupt
            handlers may not allocate memory; see :ref:`isr_rules`.

        Returns an irq object.

        Due to limitations of the hardware not all trigger events are available on all ports.
        """
        ...

    def sendbreak(self) -> None:
        """
        Send a break condition on the bus. This drives the bus low for a duration
        longer than required for a normal transmission of a character.
        """
        ...

    def deinit(self) -> None:
        """
        Turn off the UART bus.

        .. note::
          You will not be able to call ``init()`` on the object after ``deinit()``.
          A new instance needs to be created in that case.
        """
        ...

    @overload
    def init(
        self,
        /,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        tx: PinLike | None = None,
        rx: PinLike | None = None,
        txbuf: int | None = None,
        rxbuf: int | None = None,
        timeout: int | None = None,
        timeout_char: int | None = None,
        invert: int | None = None,
    ) -> None:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *rts* specifies the RTS (output) pin to use for hardware receive flow control.
          - *cts* specifies the CTS (input) pin to use for hardware transmit flow control.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

              - ``0`` will not invert lines (idle state of both lines is logic high).
              - ``UART.INV_TX`` will invert TX line (idle state of TX line now logic low).
              - ``UART.INV_RX`` will invert RX line (idle state of RX line now logic low).
              - ``UART.INV_TX | UART.INV_RX`` will invert both lines (idle state at logic low).

          - *flow* specifies which hardware flow control signals to use. The value
            is a bitmask.

              - ``0`` will ignore hardware flow control signals.
              - ``UART.RTS`` will enable receive flow control by using the RTS output pin to
                signal if the receive FIFO has sufficient space to accept more data.
              - ``UART.CTS`` will enable transmit flow control by pausing transmission when the
                CTS input pin signals that the receiver is running low on buffer space.
              - ``UART.RTS | UART.CTS`` will enable both, for full hardware flow control.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.

        .. note::
          It is possible to call ``init()`` multiple times on the same object in
          order to reconfigure  UART on the fly. That allows using single UART
          peripheral to serve different devices attached to different GPIO pins.
          Only one device can be served at a time in that case.
          Also do not call ``deinit()`` as it will prevent calling ``init()``
          again.
        """

    @overload
    def init(
        self,
        /,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        pins: tuple[PinLike, PinLike] | None = None,
    ) -> None:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *rts* specifies the RTS (output) pin to use for hardware receive flow control.
          - *cts* specifies the CTS (input) pin to use for hardware transmit flow control.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

              - ``0`` will not invert lines (idle state of both lines is logic high).
              - ``UART.INV_TX`` will invert TX line (idle state of TX line now logic low).
              - ``UART.INV_RX`` will invert RX line (idle state of RX line now logic low).
              - ``UART.INV_TX | UART.INV_RX`` will invert both lines (idle state at logic low).

          - *flow* specifies which hardware flow control signals to use. The value
            is a bitmask.

              - ``0`` will ignore hardware flow control signals.
              - ``UART.RTS`` will enable receive flow control by using the RTS output pin to
                signal if the receive FIFO has sufficient space to accept more data.
              - ``UART.CTS`` will enable transmit flow control by pausing transmission when the
                CTS input pin signals that the receiver is running low on buffer space.
              - ``UART.RTS | UART.CTS`` will enable both, for full hardware flow control.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.

        .. note::
          It is possible to call ``init()`` multiple times on the same object in
          order to reconfigure  UART on the fly. That allows using single UART
          peripheral to serve different devices attached to different GPIO pins.
          Only one device can be served at a time in that case.
          Also do not call ``deinit()`` as it will prevent calling ``init()``
          again.
        """

    @overload
    def init(
        self,
        /,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        pins: tuple[PinLike, PinLike, PinLike, PinLike] | None = None,
    ) -> None:
        """
        Initialise the UART bus with the given parameters:

          - *baudrate* is the clock rate.
          - *bits* is the number of bits per character, 7, 8 or 9.
          - *parity* is the parity, ``None``, 0 (even) or 1 (odd).
          - *stop* is the number of stop bits, 1 or 2.

        Additional keyword-only parameters that may be supported by a port are:

          - *tx* specifies the TX pin to use.
          - *rx* specifies the RX pin to use.
          - *rts* specifies the RTS (output) pin to use for hardware receive flow control.
          - *cts* specifies the CTS (input) pin to use for hardware transmit flow control.
          - *txbuf* specifies the length in characters of the TX buffer.
          - *rxbuf* specifies the length in characters of the RX buffer.
          - *timeout* specifies the time to wait for the first character (in ms).
          - *timeout_char* specifies the time to wait between characters (in ms).
          - *invert* specifies which lines to invert.

              - ``0`` will not invert lines (idle state of both lines is logic high).
              - ``UART.INV_TX`` will invert TX line (idle state of TX line now logic low).
              - ``UART.INV_RX`` will invert RX line (idle state of RX line now logic low).
              - ``UART.INV_TX | UART.INV_RX`` will invert both lines (idle state at logic low).

          - *flow* specifies which hardware flow control signals to use. The value
            is a bitmask.

              - ``0`` will ignore hardware flow control signals.
              - ``UART.RTS`` will enable receive flow control by using the RTS output pin to
                signal if the receive FIFO has sufficient space to accept more data.
              - ``UART.CTS`` will enable transmit flow control by pausing transmission when the
                CTS input pin signals that the receiver is running low on buffer space.
              - ``UART.RTS | UART.CTS`` will enable both, for full hardware flow control.

        On the WiPy only the following keyword-only parameter is supported:

          - *pins* is a 4 or 2 item list indicating the TX, RX, RTS and CTS pins (in that order).
            Any of the pins can be None if one wants the UART to operate with limited functionality.
            If the RTS pin is given the RX pin must be given as well. The same applies to CTS.
            When no pins are given, then the default set of TX and RX pins is taken, and hardware
            flow control will be disabled. If *pins* is ``None``, no pin assignment will be made.

        .. note::
          It is possible to call ``init()`` multiple times on the same object in
          order to reconfigure  UART on the fly. That allows using single UART
          peripheral to serve different devices attached to different GPIO pins.
          Only one device can be served at a time in that case.
          Also do not call ``deinit()`` as it will prevent calling ``init()``
          again.
        """

    def flush(self) -> Incomplete:
        """
        Waits until all data has been sent. In case of a timeout, an exception is raised. The timeout
        duration depends on the tx buffer size and the baud rate. Unless flow control is enabled, a timeout
        should not occur.

        .. note::

            For the esp8266 and nrf ports the call returns while the last byte is sent.
            If required, a one character wait time has to be added in the calling script.

        Availability: rp2, esp32, esp8266, mimxrt, cc3200, stm32, nrf ports, renesas-ra
        """
        ...

    def txdone(self) -> bool:
        """
        Tells whether all data has been sent or no data transfer is happening. In this case,
        it returns ``True``. If a data transmission is ongoing it returns ``False``.

        .. note::

            For the esp8266 and nrf ports the call may return ``True`` even if the last byte
            of a transfer is still being sent. If required, a one character wait time has to be
            added in the calling script.

        Availability: rp2, esp32, esp8266, mimxrt, cc3200, stm32, nrf ports, renesas-ra
        """
        ...

    @overload
    def read(self) -> bytes | None:
        """
        Read characters.  If ``nbytes`` is specified then read at most that many bytes,
        otherwise read as much data as possible. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: a bytes object containing the bytes read in.  Returns ``None``
        on timeout.
        """

    @overload
    def read(self, nbytes: int, /) -> bytes | None:
        """
        Read characters.  If ``nbytes`` is specified then read at most that many bytes,
        otherwise read as much data as possible. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: a bytes object containing the bytes read in.  Returns ``None``
        on timeout.
        """

    def any(self) -> int:
        """
        Returns an integer counting the number of characters that can be read without
        blocking.  It will return 0 if there are no characters available and a positive
        number if there are characters.  The method may return 1 even if there is more
        than one character available for reading.

        For more sophisticated querying of available characters use select.poll::

         poll = select.poll()
         poll.register(uart, select.POLLIN)
         poll.poll(timeout)
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> Union[int, None]:
        """
        Write the buffer of bytes to the bus.

        Return value: number of bytes written or ``None`` on timeout.
        """
        ...

    @overload
    def readinto(self, buf: AnyWritableBuf, /) -> int | None:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, nbytes: int, /) -> int | None:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """

    def readline(self) -> Union[str, None]:
        """
        Read a line, ending in a newline character. It may return sooner if a timeout
        is reached. The timeout is configurable in the constructor.

        Return value: the line read or ``None`` on timeout.
        """
        ...

    @overload
    def __init__(
        self,
        id: ID_T,
        /,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        tx: PinLike | None = None,
        rx: PinLike | None = None,
        txbuf: int | None = None,
        rxbuf: int | None = None,
        timeout: int | None = None,
        timeout_char: int | None = None,
        invert: int | None = None,
    ):
        """
        Construct a UART object of the given id.
        """

    @overload
    def __init__(
        self,
        id: ID_T,
        /,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        pins: tuple[PinLike, PinLike] | None = None,
    ):
        """
        Construct a UART object of the given id from a tuple of two pins.
        """

    @overload
    def __init__(
        self,
        id: ID_T,
        /,
        baudrate: int = 9600,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        pins: tuple[PinLike, PinLike, PinLike, PinLike] | None = None,
    ):
        """
        Construct a UART object of the given id from a tuple of four pins.
        """

mem32: Incomplete  ## <class 'mem'> = <32-bit memory>
mem16: Incomplete  ## <class 'mem'> = <16-bit memory>

class ADCBlock:
    """
    Access the ADC peripheral identified by *id*, which may be an integer
    or string.

    The *bits* argument, if given, sets the resolution in bits of the
    conversion process.  If not specified then the previous or default
    resolution is used.
    """

    def init(self, *, bits) -> None:
        """
        Configure the ADC peripheral.  *bits* will set the resolution of the
        conversion process.
        """
        ...

    def connect(self, channel, source, *args, **kwargs) -> Incomplete:
        """
        Connect up a channel on the ADC peripheral so it is ready for sampling,
        and return an :ref:`ADC <machine.ADC>` object that represents that connection.

        The *channel* argument must be an integer, and *source* must be an object
        (for example a :ref:`Pin <machine.Pin>`) which can be connected up for sampling.

        If only *channel* is given then it is configured for sampling.

        If only *source* is given then that object is connected to a default
        channel ready for sampling.

        If both *channel* and *source* are given then they are connected together
        and made ready for sampling.

        Any additional keyword arguments are used to configure the returned ADC object,
        via its :meth:`init <machine.ADC.init>` method.
        """
        ...

    def __init__(self, id, *, bits) -> None: ...

class ADC:
    """
    The ADC class provides an interface to analog-to-digital convertors, and
    represents a single endpoint that can sample a continuous voltage and
    convert it to a discretised value.

    Example usage::

       import machine

       adc = machine.ADC(pin)   # create an ADC object acting on a pin
       val = adc.read_u16()     # read a raw analog value in the range 0-65535
    """

    ATTN_6DB: Final[int] = 2
    WIDTH_10BIT: Final[int] = 10
    WIDTH_11BIT: Final[int] = 11
    WIDTH_12BIT: Final[int] = 12
    WIDTH_9BIT: Final[int] = 9
    ATTN_0DB: Final[int] = 0
    ATTN_2_5DB: Final[int] = 1
    ATTN_11DB: Final[int] = 3
    VREF: int = ...
    CORE_VREF: int = ...
    CORE_VBAT: int = ...
    CORE_TEMP: int = ...
    def read_u16(self) -> int:
        """
        Take an analog reading and return an integer in the range 0-65535.
        The return value represents the raw reading taken by the ADC, scaled
        such that the minimum value is 0 and the maximum value is 65535.
        """
        ...

    def init(self, *, sample_ns, atten) -> Incomplete:
        """
        Apply the given settings to the ADC.  Only those arguments that are
        specified will be changed.  See the ADC constructor above for what the
        arguments are.
        """
        ...

    def read_uv(self) -> int:
        """
        Take an analog reading and return an integer value with units of
        microvolts.  It is up to the particular port whether or not this value
        is calibrated, and how calibration is done.
        """
        ...

    def width(self, *args, **kwargs) -> Incomplete: ...
    def read(self, *args, **kwargs) -> Incomplete: ...
    def block(self) -> Incomplete:
        """
        Return the :ref:`ADCBlock <machine.ADCBlock>` instance associated with
        this ADC object.

        This method only exists if the port supports the
        :ref:`ADCBlock <machine.ADCBlock>` class.
        """
        ...

    def atten(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, pin: PinLike, /) -> None:
        """
        Access the ADC associated with a source identified by *id*.  This
        *id* may be an integer (usually specifying a channel number), a
        :ref:`Pin <machine.Pin>` object, or other value supported by the
        underlying machine.
        .. note::

        WiPy has a custom implementation of ADC, see ADCWiPy for details.
        """

class I2S:
    """
    I2S is a synchronous serial protocol used to connect digital audio devices.
    At the physical level, a bus consists of 3 lines: SCK, WS, SD.
    The I2S class supports controller operation.  Peripheral operation is not supported.

    The I2S class is currently available as a Technical Preview.  During the preview period, feedback from
    users is encouraged.  Based on this feedback, the I2S class API and implementation may be changed.

    I2S objects can be created and initialized using::

        from machine import I2S
        from machine import Pin

        # ESP32
        sck_pin = Pin(14)   # Serial clock output
        ws_pin = Pin(13)    # Word clock output
        sd_pin = Pin(12)    # Serial data output

        or

        # PyBoards
        sck_pin = Pin("Y6")   # Serial clock output
        ws_pin = Pin("Y5")    # Word clock output
        sd_pin = Pin("Y8")    # Serial data output

        audio_out = I2S(2,
                        sck=sck_pin, ws=ws_pin, sd=sd_pin,
                        mode=I2S.TX,
                        bits=16,
                        format=I2S.MONO,
                        rate=44100,
                        ibuf=20000)

        audio_in = I2S(2,
                       sck=sck_pin, ws=ws_pin, sd=sd_pin,
                       mode=I2S.RX,
                       bits=32,
                       format=I2S.STEREO,
                       rate=22050,
                       ibuf=20000)

    3 modes of operation are supported:
     - blocking
     - non-blocking
     - uasyncio

    blocking::

       num_written = audio_out.write(buf) # blocks until buf emptied

       num_read = audio_in.readinto(buf) # blocks until buf filled

    non-blocking::

       audio_out.irq(i2s_callback)         # i2s_callback is called when buf is emptied
       num_written = audio_out.write(buf)  # returns immediately

       audio_in.irq(i2s_callback)          # i2s_callback is called when buf is filled
       num_read = audio_in.readinto(buf)   # returns immediately

    uasyncio::

       swriter = uasyncio.StreamWriter(audio_out)
       swriter.write(buf)
       await swriter.drain()

       sreader = uasyncio.StreamReader(audio_in)
       num_read = await sreader.readinto(buf)
    """

    RX: Final[int] = 1
    MONO: Final[int] = 0
    STEREO: Final[int] = 1
    TX: Final[int] = 2
    @staticmethod
    def shift(
        buf: AnyWritableBuf,
        bits: int,
        shift: int,
        /,
    ) -> None:
        """
        bitwise shift of all samples contained in ``buf``. ``bits`` specifies sample size in bits. ``shift`` specifies the number of bits to shift each sample.
        Positive for left shift, negative for right shift.
        Typically used for volume control.  Each bit shift changes sample volume by 6dB.
        """
        ...

    def init(
        self,
        *,
        sck: PinLike,
        ws: PinLike,
        sd: PinLike,
        mode: int,
        bits: int,
        format: int,
        rate: int,
        ibuf: int,
    ) -> None:
        """
        see Constructor for argument descriptions
        """
        ...

    def irq(
        self,
        handler: Callable[[], None],
        /,
    ) -> None:
        """
        Set a callback. ``handler`` is called when ``buf`` is emptied (``write`` method) or becomes full (``readinto`` method).
        Setting a callback changes the ``write`` and ``readinto`` methods to non-blocking operation.
        ``handler`` is called in the context of the MicroPython scheduler.
        """
        ...

    def readinto(
        self,
        buf: AnyWritableBuf,
        /,
    ) -> int:
        """
        Read audio samples into the buffer specified by ``buf``.  ``buf`` must support the buffer protocol, such as bytearray or array.
        "buf" byte ordering is little-endian.  For Stereo format, left channel sample precedes right channel sample. For Mono format,
        the left channel sample data is used.
        Returns number of bytes read
        """
        ...

    def deinit(self) -> None:
        """
        Deinitialize the I2S bus
        """
        ...

    def write(
        self,
        buf: AnyReadableBuf,
        /,
    ) -> int:
        """
        Write audio samples contained in ``buf``. ``buf`` must support the buffer protocol, such as bytearray or array.
        "buf" byte ordering is little-endian.  For Stereo format, left channel sample precedes right channel sample. For Mono format,
        the sample data is written to both the right and left channels.
        Returns number of bytes written
        """
        ...

    def __init__(
        self,
        id: ID_T,
        /,
        *,
        sck: PinLike,
        ws: PinLike,
        sd: PinLike,
        mode: int,
        bits: int,
        format: int,
        rate: int,
        ibuf: int,
    ) -> None:
        """
        Construct an I2S object of the given id:

        - ``id`` identifies a particular I2S bus.

        ``id`` is board and port specific:

          - PYBv1.0/v1.1: has one I2S bus with id=2.
          - PYBD-SFxW: has two I2S buses with id=1 and id=2.
          - ESP32: has two I2S buses with id=0 and id=1.

        Keyword-only parameters that are supported on all ports:

          - ``sck`` is a pin object for the serial clock line
          - ``ws`` is a pin object for the word select line
          - ``sd`` is a pin object for the serial data line
          - ``mode`` specifies receive or transmit
          - ``bits`` specifies sample size (bits), 16 or 32
          - ``format`` specifies channel format, STEREO or MONO
          - ``rate`` specifies audio sampling rate (samples/s)
          - ``ibuf`` specifies internal buffer length (bytes)

        For all ports, DMA runs continuously in the background and allows user applications to perform other operations while
        sample data is transfered between the internal buffer and the I2S peripheral unit.
        Increasing the size of the internal buffer has the potential to increase the time that user applications can perform non-I2S operations
        before underflow (e.g. ``write`` method) or overflow (e.g. ``readinto`` method).
        """

class DAC:
    def write(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...

class I2C:
    """
    I2C is a two-wire protocol for communicating between devices.  At the physical
    level it consists of 2 wires: SCL and SDA, the clock and data lines respectively.

    I2C objects are created attached to a specific bus.  They can be initialised
    when created, or initialised later on.

    Printing the I2C object gives you information about its configuration.

    Both hardware and software I2C implementations exist via the
    :ref:`machine.I2C <machine.I2C>` and `machine.SoftI2C` classes.  Hardware I2C uses
    underlying hardware support of the system to perform the reads/writes and is
    usually efficient and fast but may have restrictions on which pins can be used.
    Software I2C is implemented by bit-banging and can be used on any pin but is not
    as efficient.  These classes have the same methods available and differ primarily
    in the way they are constructed.

    Example usage::

        from machine import I2C

        i2c = I2C(freq=400000)          # create I2C peripheral at frequency of 400kHz
                                        # depending on the port, extra parameters may be required
                                        # to select the peripheral and/or pins to use

        i2c.scan()                      # scan for peripherals, returning a list of 7-bit addresses

        i2c.writeto(42, b'123')         # write 3 bytes to peripheral with 7-bit address 42
        i2c.readfrom(42, 4)             # read 4 bytes from peripheral with 7-bit address 42

        i2c.readfrom_mem(42, 8, 3)      # read 3 bytes from memory of peripheral 42,
                                        #   starting at memory-address 8 in the peripheral
        i2c.writeto_mem(42, 2, b'\x10') # write 1 byte to memory of peripheral 42
                                        #   starting at address 2 in the peripheral
    """

    def readfrom_mem_into(self, addr: int, memaddr: int, buf: AnyWritableBuf, /, *, addrsize: int = 8) -> None:
        """
        Read into *buf* from the peripheral specified by *addr* starting from the
        memory address specified by *memaddr*.  The number of bytes read is the
        length of *buf*.
        The argument *addrsize* specifies the address size in bits (on ESP8266
        this argument is not recognised and the address size is always 8 bits).

        The method returns ``None``.
        """
        ...

    def readfrom_into(self, addr: int, buf: AnyWritableBuf, stop: bool = True, /) -> None:
        """
        Read into *buf* from the peripheral specified by *addr*.
        The number of bytes read will be the length of *buf*.
        If *stop* is true then a STOP condition is generated at the end of the transfer.

        The method returns ``None``.
        """
        ...

    def readfrom_mem(self, addr: int, memaddr: int, nbytes: int, /, *, addrsize: int = 8) -> bytes:
        """
        Read *nbytes* from the peripheral specified by *addr* starting from the memory
        address specified by *memaddr*.
        The argument *addrsize* specifies the address size in bits.
        Returns a `bytes` object with the data read.
        """
        ...

    def writeto_mem(self, addr: int, memaddr: int, buf: AnyReadableBuf, /, *, addrsize: int = 8) -> None:
        """
        Write *buf* to the peripheral specified by *addr* starting from the
        memory address specified by *memaddr*.
        The argument *addrsize* specifies the address size in bits (on ESP8266
        this argument is not recognised and the address size is always 8 bits).

        The method returns ``None``.
        """
        ...

    def scan(self) -> List:
        """
        Scan all I2C addresses between 0x08 and 0x77 inclusive and return a list of
        those that respond.  A device responds if it pulls the SDA line low after
        its address (including a write bit) is sent on the bus.
        """
        ...

    def writeto(self, addr: int, buf: AnyReadableBuf, stop: bool = True, /) -> int:
        """
        Write the bytes from *buf* to the peripheral specified by *addr*.  If a
        NACK is received following the write of a byte from *buf* then the
        remaining bytes are not sent.  If *stop* is true then a STOP condition is
        generated at the end of the transfer, even if a NACK is received.
        The function returns the number of ACKs that were received.
        """
        ...

    def writevto(self, addr: int, vector: Sequence[AnyReadableBuf], stop: bool = True, /) -> int:
        """
        Write the bytes contained in *vector* to the peripheral specified by *addr*.
        *vector* should be a tuple or list of objects with the buffer protocol.
        The *addr* is sent once and then the bytes from each object in *vector*
        are written out sequentially.  The objects in *vector* may be zero bytes
        in length in which case they don't contribute to the output.

        If a NACK is received following the write of a byte from one of the
        objects in *vector* then the remaining bytes, and any remaining objects,
        are not sent.  If *stop* is true then a STOP condition is generated at
        the end of the transfer, even if a NACK is received.  The function
        returns the number of ACKs that were received.
        """
        ...

    def start(self) -> None:
        """
        Generate a START condition on the bus (SDA transitions to low while SCL is high).
        """
        ...

    def readfrom(self, addr: int, nbytes: int, stop: bool = True, /) -> bytes:
        """
        Read *nbytes* from the peripheral specified by *addr*.
        If *stop* is true then a STOP condition is generated at the end of the transfer.
        Returns a `bytes` object with the data read.
        """
        ...

    def readinto(self, buf: AnyWritableBuf, nack: bool = True, /) -> None:
        """
        Reads bytes from the bus and stores them into *buf*.  The number of bytes
        read is the length of *buf*.  An ACK will be sent on the bus after
        receiving all but the last byte.  After the last byte is received, if *nack*
        is true then a NACK will be sent, otherwise an ACK will be sent (and in this
        case the peripheral assumes more bytes are going to be read in a later call).
        """
        ...

    @overload
    def init(self, *, freq: int = 400_000) -> None:
        """
        Initialise the I2C bus with the given arguments:

           - *scl* is a pin object for the SCL line
           - *sda* is a pin object for the SDA line
           - *freq* is the SCL clock rate

         In the case of hardware I2C the actual clock frequency may be lower than the
         requested frequency. This is dependent on the platform hardware. The actual
         rate may be determined by printing the I2C object.
        """

    @overload
    def init(self, *, scl: PinLike, sda: PinLike, freq: int = 400_000) -> None:
        """
        Initialise the I2C bus with the given arguments:

           - *scl* is a pin object for the SCL line
           - *sda* is a pin object for the SDA line
           - *freq* is the SCL clock rate

         In the case of hardware I2C the actual clock frequency may be lower than the
         requested frequency. This is dependent on the platform hardware. The actual
         rate may be determined by printing the I2C object.
        """

    def stop(self) -> None:
        """
        Generate a STOP condition on the bus (SDA transitions to high while SCL is high).
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> int:
        """
        Write the bytes from *buf* to the bus.  Checks that an ACK is received
        after each byte and stops transmitting the remaining bytes if a NACK is
        received.  The function returns the number of ACKs that were received.
        """
        ...

    @overload
    def __init__(self, id: ID_T, /, *, freq: int = 400_000):
        """
        Construct and return a new I2C object using the following parameters:

           - *id* identifies a particular I2C peripheral.  Allowed values for
             depend on the particular port/board
           - *scl* should be a pin object specifying the pin to use for SCL.
           - *sda* should be a pin object specifying the pin to use for SDA.
           - *freq* should be an integer which sets the maximum frequency
             for SCL.

        Note that some ports/boards will have default values of *scl* and *sda*
        that can be changed in this constructor.  Others will have fixed values
        of *scl* and *sda* that cannot be changed.
        """

    @overload
    def __init__(self, id: ID_T, /, *, scl: PinLike, sda: PinLike, freq: int = 400_000):
        """
        Construct and return a new I2C object using the following parameters:

           - *id* identifies a particular I2C peripheral.  Allowed values for
             depend on the particular port/board
           - *scl* should be a pin object specifying the pin to use for SCL.
           - *sda* should be a pin object specifying the pin to use for SDA.
           - *freq* should be an integer which sets the maximum frequency
             for SCL.

        Note that some ports/boards will have default values of *scl* and *sda*
        that can be changed in this constructor.  Others will have fixed values
        of *scl* and *sda* that cannot be changed.
        """

    @overload
    def __init__(self, *, scl: PinLike, sda: PinLike, freq: int = 400_000) -> None:
        """
        Initialise the I2C bus with the given arguments:

           - *scl* is a pin object for the SCL line
           - *sda* is a pin object for the SDA line
           - *freq* is the SCL clock rate

         In the case of hardware I2C the actual clock frequency may be lower than the
         requested frequency. This is dependent on the platform hardware. The actual
         rate may be determined by printing the I2C object.
        """

class Timer:
    """
    Hardware timers deal with timing of periods and events. Timers are perhaps
    the most flexible and heterogeneous kind of hardware in MCUs and SoCs,
    differently greatly from a model to a model. MicroPython's Timer class
    defines a baseline operation of executing a callback with a given period
    (or once after some delay), and allow specific boards to define more
    non-standard behaviour (which thus won't be portable to other boards).

    See discussion of :ref:`important constraints <machine_callbacks>` on
    Timer callbacks.

    .. note::

        Memory can't be allocated inside irq handlers (an interrupt) and so
        exceptions raised within a handler don't give much information.  See
        :func:`micropython.alloc_emergency_exception_buf` for how to get around this
        limitation.

    If you are using a WiPy board please refer to :ref:`machine.TimerWiPy <machine.TimerWiPy>`
    instead of this class.
    """

    ONE_SHOT: Final[int] = 0
    PERIODIC: Final[int] = 1
    def deinit(self) -> None:
        """
        Deinitialises the timer. Stops the timer, and disables the timer peripheral.
        """
        ...

    @overload
    def init(
        self,
        *,
        mode: int = PERIODIC,
        period: int | None = None,
        callback: Callable[[Timer], None] | None = None,
    ) -> None: ...
    @overload
    def init(
        self,
        *,
        mode: int = PERIODIC,
        freq: int | None = None,
        callback: Callable[[Timer], None] | None = None,
    ) -> None: ...
    @overload
    def init(
        self,
        *,
        mode: int = PERIODIC,
        tick_hz: int | None = None,
        callback: Callable[[Timer], None] | None = None,
    ) -> None:
        """
        Initialise the timer. Example::

            def mycallback(t):
                pass

            # periodic at 1kHz
            tim.init(mode=Timer.PERIODIC, freq=1000, callback=mycallback)

            # periodic with 100ms period
            tim.init(period=100, callback=mycallback)

            # one shot firing after 1000ms
            tim.init(mode=Timer.ONE_SHOT, period=1000, callback=mycallback)

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.ONE_SHOT`` - The timer runs once until the configured
              period of the channel expires.
            - ``Timer.PERIODIC`` - The timer runs periodically at the configured
              frequency of the channel.

          - ``freq`` - The timer frequency, in units of Hz.  The upper bound of
            the frequency is dependent on the port.  When both the ``freq`` and
            ``period`` arguments are given, ``freq`` has a higher priority and
            ``period`` is ignored.

          - ``period`` - The timer period, in milliseconds.

          - ``callback`` - The callable to call upon expiration of the timer period.
            The callback must take one argument, which is passed the Timer object.
            The ``callback`` argument shall be specified. Otherwise an exception
            will occur upon timer expiration:
            ``TypeError: 'NoneType' object isn't callable``
        """
        ...

    def value(self, *args, **kwargs) -> Incomplete: ...
    @overload
    def __init__(self, id: int, /):
        """
        Construct a new timer object of the given ``id``. ``id`` of -1 constructs a
        virtual timer (if supported by a board).
        ``id`` shall not be passed as a keyword argument.

        See ``init`` for parameters of initialisation.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        *,
        mode: int = PERIODIC,
        period: int | None = None,
        callback: Callable[[Timer], None] | None = None,
    ):
        """
        Construct a new timer object of the given ``id``. ``id`` of -1 constructs a
        virtual timer (if supported by a board).
        ``id`` shall not be passed as a keyword argument.

        See ``init`` for parameters of initialisation.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        *,
        mode: int = PERIODIC,
        freq: int | None = None,
        callback: Callable[[Timer], None] | None = None,
    ):
        """
        Construct a new timer object of the given ``id``. ``id`` of -1 constructs a
        virtual timer (if supported by a board).
        ``id`` shall not be passed as a keyword argument.

        See ``init`` for parameters of initialisation.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        *,
        mode: int = PERIODIC,
        tick_hz: int | None = None,
        callback: Callable[[Timer], None] | None = None,
    ):
        """
        Construct a new timer object of the given ``id``. ``id`` of -1 constructs a
        virtual timer (if supported by a board).
        ``id`` shall not be passed as a keyword argument.

        See ``init`` for parameters of initialisation.
        """

class SoftSPI(SPI):
    """
    Construct a new software SPI object.  Additional parameters must be
    given, usually at least *sck*, *mosi* and *miso*, and these are used
    to initialise the bus.  See `SPI.init` for a description of the parameters.
    """

    LSB: Final[int] = 1
    MSB: Final[int] = 0
    def deinit(self, *args, **kwargs) -> Incomplete: ...
    def init(self, *args, **kwargs) -> Incomplete: ...
    def write_readinto(self, *args, **kwargs) -> Incomplete: ...
    def read(self, *args, **kwargs) -> Incomplete: ...
    def write(self, *args, **kwargs) -> Incomplete: ...
    def readinto(self, *args, **kwargs) -> Incomplete: ...
    def __init__(
        self,
        baudrate=500000,
        *,
        polarity=0,
        phase=0,
        bits=8,
        firstbit=MSB,
        sck: PinLike | None = None,
        mosi: PinLike | None = None,
        miso: PinLike | None = None,
    ) -> None: ...

class Pin:
    """
    A pin object is used to control I/O pins (also known as GPIO - general-purpose
    input/output).  Pin objects are commonly associated with a physical pin that can
    drive an output voltage and read input voltages.  The pin class has methods to set the mode of
    the pin (IN, OUT, etc) and methods to get and set the digital logic level.
    For analog control of a pin, see the :class:`ADC` class.

    A pin object is constructed by using an identifier which unambiguously
    specifies a certain I/O pin.  The allowed forms of the identifier and the
    physical pin that the identifier maps to are port-specific.  Possibilities
    for the identifier are an integer, a string or a tuple with port and pin
    number.

    Usage Model::

        from machine import Pin

        # create an output pin on pin #0
        p0 = Pin(0, Pin.OUT)

        # set the value low then high
        p0.value(0)
        p0.value(1)

        # create an input pin on pin #2, with a pull up resistor
        p2 = Pin(2, Pin.IN, Pin.PULL_UP)

        # read and print the pin value
        print(p2.value())

        # reconfigure pin #0 in input mode with a pull down resistor
        p0.init(p0.IN, p0.PULL_DOWN)

        # configure an irq callback
        p0.irq(lambda p:print(p))
    """

    OPEN_DRAIN: Final[int] = 7
    OUT: Final[int] = 3
    IRQ_RISING: Final[int] = 1
    WAKE_LOW: Final[int] = 4
    WAKE_HIGH: Final[int] = 5
    PULL_DOWN: Final[int] = 1
    PULL_UP: Final[int] = 2
    DRIVE_1: Final[int] = 1
    IRQ_FALLING: Final[int] = 2
    DRIVE_0: Final[int] = 0
    IN: Final[int] = 1
    DRIVE_2: Final[int] = 2
    DRIVE_3: Final[int] = 3
    ALT: Incomplete
    ALT_OPEN_DRAIN: Incomplete
    ANALOG: Incomplete
    PULL_HOLD: Incomplete
    IRQ_LOW_LEVEL: Incomplete
    IRQ_HIGH_LEVEL: Incomplete
    def off(self) -> None:
        """
        Set pin to "0" output level.
        """
        ...

    def irq(
        self,
        /,
        handler: Callable[[Pin], None] | None = None,
        trigger: int = (IRQ_FALLING | IRQ_RISING),
        *,
        priority: int = 1,
        wake: int | None = None,
        hard: bool = False,
    ) -> Callable[..., Incomplete]:
        """
           Configure an interrupt handler to be called when the trigger source of the
           pin is active.  If the pin mode is ``Pin.IN`` then the trigger source is
           the external value on the pin.  If the pin mode is ``Pin.OUT`` then the
           trigger source is the output buffer of the pin.  Otherwise, if the pin mode
           is ``Pin.OPEN_DRAIN`` then the trigger source is the output buffer for
           state '0' and the external pin value for state '1'.

           The arguments are:

             - ``handler`` is an optional function to be called when the interrupt
               triggers. The handler must take exactly one argument which is the
               ``Pin`` instance.

             - ``trigger`` configures the event which can generate an interrupt.
               Possible values are:

               - ``Pin.IRQ_FALLING`` interrupt on falling edge.
               - ``Pin.IRQ_RISING`` interrupt on rising edge.
               - ``Pin.IRQ_LOW_LEVEL`` interrupt on low level.
               - ``Pin.IRQ_HIGH_LEVEL`` interrupt on high level.

               These values can be OR'ed together to trigger on multiple events.

             - ``priority`` sets the priority level of the interrupt.  The values it
               can take are port-specific, but higher values always represent higher
               priorities.

             - ``wake`` selects the power mode in which this interrupt can wake up the
               system.  It can be ``machine.IDLE``, ``machine.SLEEP`` or ``machine.DEEPSLEEP``.
               These values can also be OR'ed together to make a pin generate interrupts in
               more than one power mode.

             - ``hard`` if true a hardware interrupt is used. This reduces the delay
               between the pin change and the handler being called. Hard interrupt
               handlers may not allocate memory; see :ref:`isr_rules`.
               Not all ports support this argument.

           This method returns a callback object.

        The following methods are not part of the core Pin API and only implemented on certain ports.
        """
        ...

    def on(self) -> None:
        """
        Set pin to "1" output level.
        """
        ...

    def toggle(self) -> Incomplete:
        """
        Toggle output pin from "0" to "1" or vice-versa.

        Availability: cc3200, esp32, esp8266, mimxrt, rp2, samd ports.
        """
        ...

    @overload
    def value(self) -> int:
        """
        This method allows to set and get the value of the pin, depending on whether
        the argument ``x`` is supplied or not.

        If the argument is omitted then this method gets the digital logic level of
        the pin, returning 0 or 1 corresponding to low and high voltage signals
        respectively.  The behaviour of this method depends on the mode of the pin:

          - ``Pin.IN`` - The method returns the actual input value currently present
            on the pin.
          - ``Pin.OUT`` - The behaviour and return value of the method is undefined.
          - ``Pin.OPEN_DRAIN`` - If the pin is in state '0' then the behaviour and
            return value of the method is undefined.  Otherwise, if the pin is in
            state '1', the method returns the actual input value currently present
            on the pin.

        If the argument is supplied then this method sets the digital logic level of
        the pin.  The argument ``x`` can be anything that converts to a boolean.
        If it converts to ``True``, the pin is set to state '1', otherwise it is set
        to state '0'.  The behaviour of this method depends on the mode of the pin:

          - ``Pin.IN`` - The value is stored in the output buffer for the pin.  The
            pin state does not change, it remains in the high-impedance state.  The
            stored value will become active on the pin as soon as it is changed to
            ``Pin.OUT`` or ``Pin.OPEN_DRAIN`` mode.
          - ``Pin.OUT`` - The output buffer is set to the given value immediately.
          - ``Pin.OPEN_DRAIN`` - If the value is '0' the pin is set to a low voltage
            state.  Otherwise the pin is set to high-impedance state.

        When setting the value this method returns ``None``.
        """

    @overload
    def value(self, x: Any, /) -> None:
        """
        This method allows to set and get the value of the pin, depending on whether
        the argument ``x`` is supplied or not.

        If the argument is omitted then this method gets the digital logic level of
        the pin, returning 0 or 1 corresponding to low and high voltage signals
        respectively.  The behaviour of this method depends on the mode of the pin:

          - ``Pin.IN`` - The method returns the actual input value currently present
            on the pin.
          - ``Pin.OUT`` - The behaviour and return value of the method is undefined.
          - ``Pin.OPEN_DRAIN`` - If the pin is in state '0' then the behaviour and
            return value of the method is undefined.  Otherwise, if the pin is in
            state '1', the method returns the actual input value currently present
            on the pin.

        If the argument is supplied then this method sets the digital logic level of
        the pin.  The argument ``x`` can be anything that converts to a boolean.
        If it converts to ``True``, the pin is set to state '1', otherwise it is set
        to state '0'.  The behaviour of this method depends on the mode of the pin:

          - ``Pin.IN`` - The value is stored in the output buffer for the pin.  The
            pin state does not change, it remains in the high-impedance state.  The
            stored value will become active on the pin as soon as it is changed to
            ``Pin.OUT`` or ``Pin.OPEN_DRAIN`` mode.
          - ``Pin.OUT`` - The output buffer is set to the given value immediately.
          - ``Pin.OPEN_DRAIN`` - If the value is '0' the pin is set to a low voltage
            state.  Otherwise the pin is set to high-impedance state.

        When setting the value this method returns ``None``.
        """

    def init(
        self,
        mode: int = -1,
        pull: int = -1,
        *,
        value: Any = None,
        drive: int | None = None,
        alt: int | None = None,
    ) -> None:
        """
        Re-initialise the pin using the given parameters.  Only those arguments that
        are specified will be set.  The rest of the pin peripheral state will remain
        unchanged.  See the constructor documentation for details of the arguments.

        Returns ``None``.
        """
        ...

    class board:
        def __init__(self, *argv, **kwargs) -> None: ...

    def __init__(
        self,
        id: Any,
        /,
        mode: int = -1,
        pull: int = -1,
        *,
        value: Any = None,
        drive: int | None = None,
        alt: int | None = None,
    ) -> None:
        """
        Access the pin peripheral (GPIO pin) associated with the given ``id``.  If
        additional arguments are given in the constructor then they are used to initialise
        the pin.  Any settings that are not specified will remain in their previous state.

        The arguments are:

          - ``id`` is mandatory and can be an arbitrary object.  Among possible value
            types are: int (an internal Pin identifier), str (a Pin name), and tuple
            (pair of [port, pin]).

          - ``mode`` specifies the pin mode, which can be one of:

            - ``Pin.IN`` - Pin is configured for input.  If viewed as an output the pin
              is in high-impedance state.

            - ``Pin.OUT`` - Pin is configured for (normal) output.

            - ``Pin.OPEN_DRAIN`` - Pin is configured for open-drain output. Open-drain
              output works in the following way: if the output value is set to 0 the pin
              is active at a low level; if the output value is 1 the pin is in a high-impedance
              state.  Not all ports implement this mode, or some might only on certain pins.

            - ``Pin.ALT`` - Pin is configured to perform an alternative function, which is
              port specific.  For a pin configured in such a way any other Pin methods
              (except :meth:`Pin.init`) are not applicable (calling them will lead to undefined,
              or a hardware-specific, result).  Not all ports implement this mode.

            - ``Pin.ALT_OPEN_DRAIN`` - The Same as ``Pin.ALT``, but the pin is configured as
              open-drain.  Not all ports implement this mode.

            - ``Pin.ANALOG`` - Pin is configured for analog input, see the :class:`ADC` class.

          - ``pull`` specifies if the pin has a (weak) pull resistor attached, and can be
            one of:

            - ``None`` - No pull up or down resistor.
            - ``Pin.PULL_UP`` - Pull up resistor enabled.
            - ``Pin.PULL_DOWN`` - Pull down resistor enabled.

          - ``value`` is valid only for Pin.OUT and Pin.OPEN_DRAIN modes and specifies initial
            output pin value if given, otherwise the state of the pin peripheral remains
            unchanged.

          - ``drive`` specifies the output power of the pin and can be one of: ``Pin.LOW_POWER``,
            ``Pin.MED_POWER`` or ``Pin.HIGH_POWER``.  The actual current driving capabilities
            are port dependent.  Not all ports implement this argument.

          - ``alt`` specifies an alternate function for the pin and the values it can take are
            port dependent.  This argument is valid only for ``Pin.ALT`` and ``Pin.ALT_OPEN_DRAIN``
            modes.  It may be used when a pin supports more than one alternate function.  If only
            one pin alternate function is supported the this argument is not required.  Not all
            ports implement this argument.

        As specified above, the Pin class allows to set an alternate function for a particular
        pin, but it does not specify any further operations on such a pin.  Pins configured in
        alternate-function mode are usually not used as GPIO but are instead driven by other
        hardware peripherals.  The only operation supported on such a pin is re-initialising,
        by calling the constructor or :meth:`Pin.init` method.  If a pin that is configured in
        alternate-function mode is re-initialised with ``Pin.IN``, ``Pin.OUT``, or
        ``Pin.OPEN_DRAIN``, the alternate function will be removed from the pin.
        """

    @overload
    def __call__(self) -> int:
        """
        Pin objects are callable.  The call method provides a (fast) shortcut to set
        and get the value of the pin.  It is equivalent to Pin.value([x]).
        See :meth:`Pin.value` for more details.
        """

    @overload
    def __call__(self, x: Any, /) -> None:
        """
        Pin objects are callable.  The call method provides a (fast) shortcut to set
        and get the value of the pin.  It is equivalent to Pin.value([x]).
        See :meth:`Pin.value` for more details.
        """

    @overload
    def mode(self) -> int:
        """
        Get or set the pin mode.
        See the constructor documentation for details of the ``mode`` argument.

        Availability: cc3200, stm32 ports.
        """

    @overload
    def mode(self, mode: int, /) -> None:
        """
        Get or set the pin mode.
        See the constructor documentation for details of the ``mode`` argument.

        Availability: cc3200, stm32 ports.
        """

    @overload
    def pull(self) -> int:
        """
        Get or set the pin pull state.
        See the constructor documentation for details of the ``pull`` argument.

        Availability: cc3200, stm32 ports.
        """

    @overload
    def pull(self, pull: int, /) -> None:
        """
        Get or set the pin pull state.
        See the constructor documentation for details of the ``pull`` argument.

        Availability: cc3200, stm32 ports.
        """

    @overload
    def drive(self, drive: int, /) -> None:
        """
        Get or set the pin drive strength.
        See the constructor documentation for details of the ``drive`` argument.

        Availability: cc3200 port.
        """
        ...

    @overload
    def drive(self, /) -> int:
        """
        Get or set the pin drive strength.
        See the constructor documentation for details of the ``drive`` argument.

        Availability: cc3200 port.
        """

class TouchPad:
    def config(self, *args, **kwargs) -> Incomplete: ...
    def read(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...

class WDT:
    """
    The WDT is used to restart the system when the application crashes and ends
    up into a non recoverable state. Once started it cannot be stopped or
    reconfigured in any way. After enabling, the application must "feed" the
    watchdog periodically to prevent it from expiring and resetting the system.

    Example usage::

        from machine import WDT
        wdt = WDT(timeout=2000)  # enable it with a timeout of 2s
        wdt.feed()

    Availability of this class: pyboard, WiPy, esp8266, esp32.
    """

    def feed(self) -> None:
        """
        Feed the WDT to prevent it from resetting the system. The application
        should place this call in a sensible place ensuring that the WDT is
        only fed after verifying that everything is functioning correctly.
        """
        ...

    def __init__(self, *, id: int = 0, timeout: int = 5000) -> None:
        """
        Create a WDT object and start it. The timeout must be given in milliseconds.
        Once it is running the timeout cannot be changed and the WDT cannot be stopped either.

        Notes: On the esp32 the minimum timeout is 1 second. On the esp8266 a timeout
        cannot be specified, it is determined by the underlying system.
        """

class SDCard(AbstractBlockDev):
    """
    SD cards are one of the most common small form factor removable storage media.
    SD cards come in a variety of sizes and physical form factors. MMC cards are
    similar removable storage devices while eMMC devices are electrically similar
    storage devices designed to be embedded into other systems. All three form
    share a common protocol for communication with their host system and high-level
    support looks the same for them all. As such in MicroPython they are implemented
    in a single class called :class:`machine.SDCard` .

    Both SD and MMC interfaces support being accessed with a variety of bus widths.
    When being accessed with a 1-bit wide interface they can be accessed using the
    SPI protocol. Different MicroPython hardware platforms support different widths
    and pin configurations but for most platforms there is a standard configuration
    for any given hardware. In general constructing an ``SDCard`` object with without
    passing any parameters will initialise the interface to the default card slot
    for the current hardware. The arguments listed below represent the common
    arguments that might need to be set in order to use either a non-standard slot
    or a non-standard pin assignment. The exact subset of arguments supported will
    vary from platform to platform.


    Implementation-specific details
    -------------------------------

    Different implementations of the ``SDCard`` class on different hardware support
    varying subsets of the options above.

    PyBoard
    ```````

    The standard PyBoard has just one slot. No arguments are necessary or supported.

    ESP32
    `````

    The ESP32 provides two channels of SD/MMC hardware and also supports
    access to SD Cards through either of the two SPI ports that are
    generally available to the user. As a result the *slot* argument can
    take a value between 0 and 3, inclusive. Slots 0 and 1 use the
    built-in SD/MMC hardware while slots 2 and 3 use the SPI ports. Slot 0
    supports 1, 4 or 8-bit wide access while slot 1 supports 1 or 4-bit
    access; the SPI slots only support 1-bit access.

      .. note:: Slot 0 is used to communicate with on-board flash memory
                on most ESP32 modules and so will be unavailable to the
                user.

      .. note:: Most ESP32 modules that provide an SD card slot using the
                dedicated hardware only wire up 1 data pin, so the default
                value for *width* is 1.

    The pins used by the dedicated SD/MMC hardware are fixed. The pins
    used by the SPI hardware can be reassigned.

      .. note:: If any of the SPI signals are remapped then all of the SPI
                signals will pass through a GPIO multiplexer unit which
                can limit the performance of high frequency signals. Since
                the normal operating speed for SD cards is 40MHz this can
                cause problems on some cards.

    The default (and preferred) pin assignment are as follows:

        ====== ====== ====== ====== ======
        Slot   0      1      2      3
        ------ ------ ------ ------ ------
        Signal   Pin    Pin    Pin    Pin
        ====== ====== ====== ====== ======
        sck       6     14     18     14
        cmd      11     15
        cs                      5     15
        miso                   19     12
        mosi                   23     13
        D0        7      2
        D1        8      4
        D2        9     12
        D3       10     13
        D4       16
        D5       17
        D6        5
        D7       18
        ====== ====== ====== ====== ======

    cc3200
    ``````

    You can set the pins used for SPI access by passing a tuple as the
    *pins* argument.

    *Note:* The current cc3200 SD card implementation names the this class
    :class:`machine.SD` rather than :class:`machine.SDCard` .
    """

    def ioctl(self, *args, **kwargs) -> Incomplete: ...
    @overload
    def readblocks(self, block_num: int, buf: bytearray) -> bool:
        """
        The first form reads aligned, multiples of blocks.
        Starting at the block given by the index *block_num*, read blocks from
        the device into *buf* (an array of bytes).
        The number of blocks to read is given by the length of *buf*,
        which will be a multiple of the block size.
        """

    @overload
    def readblocks(self, block_num: int, buf: bytearray, offset: int) -> bool:
        """
        The second form allows reading at arbitrary locations within a block,
        and arbitrary lengths.
        Starting at block index *block_num*, and byte offset within that block
        of *offset*, read bytes from the device into *buf* (an array of bytes).
        The number of bytes to read is given by the length of *buf*.
        """

    @overload
    def writeblocks(self, block_num: int, buf: bytes | bytearray, /) -> None:
        """
        The first form writes aligned, multiples of blocks, and requires that the
        blocks that are written to be first erased (if necessary) by this method.
        Starting at the block given by the index *block_num*, write blocks from
        *buf* (an array of bytes) to the device.
        The number of blocks to write is given by the length of *buf*,
        which will be a multiple of the block size.
        """

    @overload
    def writeblocks(self, block_num: int, buf: bytes | bytearray, offset: int, /) -> None:
        """
        The second form allows writing at arbitrary locations within a block,
        and arbitrary lengths.  Only the bytes being written should be changed,
        and the caller of this method must ensure that the relevant blocks are
        erased via a prior ``ioctl`` call.
        Starting at block index *block_num*, and byte offset within that block
        of *offset*, write bytes from *buf* (an array of bytes) to the device.
        The number of bytes to write is given by the length of *buf*.

        Note that implementations must never implicitly erase blocks if the offset
        argument is specified, even if it is zero.
        """

    def info(self, *args, **kwargs) -> Incomplete: ...
    def deinit(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...

class RTC:
    """
    The RTC is an independent clock that keeps track of the date
    and time.

    Example usage::

        rtc = machine.RTC()
        rtc.datetime((2020, 1, 21, 2, 10, 32, 36, 0))
        print(rtc.datetime())



    The documentation for RTC is in a poor state;1
    """

    ALARM0: Incomplete

    @overload
    def init(self) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    @overload
    def init(self, datetime: tuple[int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    @overload
    def init(self, datetime: tuple[int, int, int, int, int, int, int, int], /) -> None:
        """
        Initialise the RTC. Datetime is a tuple of the form:

           ``(year, month, day, hour, minute, second, microsecond, tzinfo)``

        All eight arguments must be present. The ``microsecond`` and ``tzinfo``
        values are currently ignored but might be used in the future.

        Availability: CC3200, ESP32, MIMXRT, SAMD. The rtc.init() method on
        the stm32 and renesas-ra ports just (re-)starts the RTC and does not
        accept arguments.
        """

    def memory(self, data: Any | None = None) -> bytes:
        """
        ``RTC.memory(data)`` will write *data* to the RTC memory, where *data* is any
        object which supports the buffer protocol (including `bytes`, `bytearray`,
        `memoryview` and `array.array`). ``RTC.memory()`` reads RTC memory and returns
        a `bytes` object.

        Data written to RTC user memory is persistent across restarts, including
        :ref:`soft_reset` and `machine.deepsleep()`.

        The maximum length of RTC user memory is 2048 bytes by default on esp32,
        and 492 bytes on esp8266.

        Availability: esp32, esp8266 ports.
        """
        ...

    def datetime(self, datetimetuple: Any | None = None) -> Tuple:
        """
        Get or set the date and time of the RTC.

        With no arguments, this method returns an 8-tuple with the current
        date and time.  With 1 argument (being an 8-tuple) it sets the date
        and time.

        The 8-tuple has the following format:

            (year, month, day, weekday, hours, minutes, seconds, subseconds)

        The meaning of the ``subseconds`` field is hardware dependent.
        """
        ...

    @overload
    def __init__(self, id: int = 0):
        """
        Create an RTC object. See init for parameters of initialization.
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def __init__(self, id: int = 0, /, *, datetime: tuple[int, int, int, int, int, int, int, int]):
        """
        Create an RTC object. See init for parameters of initialization.

        The documentation for RTC is in a poor state; better to experiment and use `dir`!
        """

    @overload
    def alarm(self, id: int, time: int, /, *, repeat: bool = False) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

    @overload
    def alarm(self, id: int, time: tuple[int, int, int, int, int, int, int, int], /) -> None:
        """
        Set the RTC alarm. Time might be either a millisecond value to program the alarm to
        current time + time_in_ms in the future, or a datetimetuple. If the time passed is in
        milliseconds, repeat can be set to ``True`` to make the alarm periodic.
        """

class SoftI2C(I2C):
    """
    Construct a new software I2C object.  The parameters are:

       - *scl* should be a pin object specifying the pin to use for SCL.
       - *sda* should be a pin object specifying the pin to use for SDA.
       - *freq* should be an integer which sets the maximum frequency
         for SCL.
       - *timeout* is the maximum time in microseconds to wait for clock
         stretching (SCL held low by another device on the bus), after
         which an ``OSError(ETIMEDOUT)`` exception is raised.
    """

    def readfrom_mem_into(self, *args, **kwargs) -> Incomplete: ...
    def readfrom_into(self, *args, **kwargs) -> Incomplete: ...
    def readfrom_mem(self, *args, **kwargs) -> Incomplete: ...
    def writeto_mem(self, *args, **kwargs) -> Incomplete: ...
    def scan(self, *args, **kwargs) -> Incomplete: ...
    def writeto(self, *args, **kwargs) -> Incomplete: ...
    def writevto(self, *args, **kwargs) -> Incomplete: ...
    def start(self, *args, **kwargs) -> Incomplete: ...
    def readfrom(self, *args, **kwargs) -> Incomplete: ...
    def readinto(self, *args, **kwargs) -> Incomplete: ...
    def init(self, *args, **kwargs) -> Incomplete: ...
    def stop(self, *args, **kwargs) -> Incomplete: ...
    def write(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, scl, sda, *, freq=400000, timeout=50000) -> None: ...

class SPI:
    """
    SPI is a synchronous serial protocol that is driven by a controller. At the
    physical level, a bus consists of 3 lines: SCK, MOSI, MISO. Multiple devices
    can share the same bus. Each device should have a separate, 4th signal,
    CS (Chip Select), to select a particular device on a bus with which
    communication takes place. Management of a CS signal should happen in
    user code (via machine.Pin class).

    Both hardware and software SPI implementations exist via the
    :ref:`machine.SPI <machine.SPI>` and `machine.SoftSPI` classes.  Hardware SPI uses underlying
    hardware support of the system to perform the reads/writes and is usually
    efficient and fast but may have restrictions on which pins can be used.
    Software SPI is implemented by bit-banging and can be used on any pin but
    is not as efficient.  These classes have the same methods available and
    differ primarily in the way they are constructed.

    Example usage::

        from machine import SPI, Pin

        spi = SPI(0, baudrate=400000)           # Create SPI peripheral 0 at frequency of 400kHz.
                                                # Depending on the use case, extra parameters may be required
                                                # to select the bus characteristics and/or pins to use.
        cs = Pin(4, mode=Pin.OUT, value=1)      # Create chip-select on pin 4.

        try:
            cs(0)                               # Select peripheral.
            spi.write(b"12345678")              # Write 8 bytes, and don't care about received data.
        finally:
            cs(1)                               # Deselect peripheral.

        try:
            cs(0)                               # Select peripheral.
            rxdata = spi.read(8, 0x42)          # Read 8 bytes while writing 0x42 for each byte.
        finally:
            cs(1)                               # Deselect peripheral.

        rxdata = bytearray(8)
        try:
            cs(0)                               # Select peripheral.
            spi.readinto(rxdata, 0x42)          # Read 8 bytes inplace while writing 0x42 for each byte.
        finally:
            cs(1)                               # Deselect peripheral.

        txdata = b"12345678"
        rxdata = bytearray(len(txdata))
        try:
            cs(0)                               # Select peripheral.
            spi.write_readinto(txdata, rxdata)  # Simultaneously write and read bytes.
        finally:
            cs(1)                               # Deselect peripheral.
    """

    LSB: Final[int] = 1
    MSB: Final[int] = 0
    CONTROLLER: Incomplete
    def deinit(self) -> None:
        """
        Turn off the SPI bus.
        """
        ...

    @overload
    def init(
        self,
        baudrate: int = 1_000_000,
        *,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        sck: PinLike | None = None,
        mosi: PinLike | None = None,
        miso: PinLike | None = None,
    ) -> None:
        """
        Initialise the SPI bus with the given parameters:

          - ``baudrate`` is the SCK clock rate.
          - ``polarity`` can be 0 or 1, and is the level the idle clock line sits at.
          - ``phase`` can be 0 or 1 to sample data on the first or second clock edge
            respectively.
          - ``bits`` is the width in bits of each transfer. Only 8 is guaranteed to be supported by all hardware.
          - ``firstbit`` can be ``SPI.MSB`` or ``SPI.LSB``.
          - ``sck``, ``mosi``, ``miso`` are pins (machine.Pin) objects to use for bus signals. For most
            hardware SPI blocks (as selected by ``id`` parameter to the constructor), pins are fixed
            and cannot be changed. In some cases, hardware blocks allow 2-3 alternative pin sets for
            a hardware SPI block. Arbitrary pin assignments are possible only for a bitbanging SPI driver
            (``id`` = -1).
          - ``pins`` - WiPy port doesn't ``sck``, ``mosi``, ``miso`` arguments, and instead allows to
            specify them as a tuple of ``pins`` parameter.

        In the case of hardware SPI the actual clock frequency may be lower than the
        requested baudrate. This is dependent on the platform hardware. The actual
        rate may be determined by printing the SPI object.
        """

    @overload
    def init(
        self,
        baudrate: int = 1_000_000,
        *,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        pins: tuple[PinLike, PinLike, PinLike] | None = None,
    ) -> None:
        """
        Initialise the SPI bus with the given parameters:

          - ``baudrate`` is the SCK clock rate.
          - ``polarity`` can be 0 or 1, and is the level the idle clock line sits at.
          - ``phase`` can be 0 or 1 to sample data on the first or second clock edge
            respectively.
          - ``bits`` is the width in bits of each transfer. Only 8 is guaranteed to be supported by all hardware.
          - ``firstbit`` can be ``SPI.MSB`` or ``SPI.LSB``.
          - ``sck``, ``mosi``, ``miso`` are pins (machine.Pin) objects to use for bus signals. For most
            hardware SPI blocks (as selected by ``id`` parameter to the constructor), pins are fixed
            and cannot be changed. In some cases, hardware blocks allow 2-3 alternative pin sets for
            a hardware SPI block. Arbitrary pin assignments are possible only for a bitbanging SPI driver
            (``id`` = -1).
          - ``pins`` - WiPy port doesn't ``sck``, ``mosi``, ``miso`` arguments, and instead allows to
            specify them as a tuple of ``pins`` parameter.

        In the case of hardware SPI the actual clock frequency may be lower than the
        requested baudrate. This is dependent on the platform hardware. The actual
        rate may be determined by printing the SPI object.
        """

    def write_readinto(self, write_buf: AnyReadableBuf, read_buf: AnyWritableBuf, /) -> int:
        """
        Write the bytes from ``write_buf`` while reading into ``read_buf``.  The
        buffers can be the same or different, but both buffers must have the
        same length.
        Returns ``None``.

        Note: on WiPy this function returns the number of bytes written.
        """
        ...

    def read(self, nbytes: int, write: int = 0x00, /) -> bytes:
        """
        Read a number of bytes specified by ``nbytes`` while continuously writing
        the single byte given by ``write``.
        Returns a ``bytes`` object with the data that was read.
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> int:
        """
        Write the bytes contained in ``buf``.
        Returns ``None``.

        Note: on WiPy this function returns the number of bytes written.
        """
        ...

    def readinto(self, buf: AnyWritableBuf, write: int = 0x00, /) -> int:
        """
        Read into the buffer specified by ``buf`` while continuously writing the
        single byte given by ``write``.
        Returns ``None``.

        Note: on WiPy this function returns the number of bytes read.
        """
        ...

    @overload
    def __init__(self, id: int, /):
        """
        Construct an SPI object on the given bus, *id*. Values of *id* depend
        on a particular port and its hardware. Values 0, 1, etc. are commonly used
        to select hardware SPI block #0, #1, etc.

        With no additional parameters, the SPI object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        baudrate: int = 1_000_000,
        *,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        sck: PinLike | None = None,
        mosi: PinLike | None = None,
        miso: PinLike | None = None,
    ):
        """
        Construct an SPI object on the given bus, *id*. Values of *id* depend
        on a particular port and its hardware. Values 0, 1, etc. are commonly used
        to select hardware SPI block #0, #1, etc.

        With no additional parameters, the SPI object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        baudrate: int = 1_000_000,
        *,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        pins: tuple[PinLike, PinLike, PinLike] | None = None,
    ):
        """
        Construct an SPI object on the given bus, *id*. Values of *id* depend
        on a particular port and its hardware. Values 0, 1, etc. are commonly used
        to select hardware SPI block #0, #1, etc.

        With no additional parameters, the SPI object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.
        """

class Signal(Pin):
    """
    The Signal class is a simple extension of the `Pin` class. Unlike Pin, which
    can be only in "absolute" 0 and 1 states, a Signal can be in "asserted"
    (on) or "deasserted" (off) states, while being inverted (active-low) or
    not. In other words, it adds logical inversion support to Pin functionality.
    While this may seem a simple addition, it is exactly what is needed to
    support wide array of simple digital devices in a way portable across
    different boards, which is one of the major MicroPython goals. Regardless
    of whether different users have an active-high or active-low LED, a normally
    open or normally closed relay - you can develop a single, nicely looking
    application which works with each of them, and capture hardware
    configuration differences in few lines in the config file of your app.

    Example::

        from machine import Pin, Signal

        # Suppose you have an active-high LED on pin 0
        led1_pin = Pin(0, Pin.OUT)
        # ... and active-low LED on pin 1
        led2_pin = Pin(1, Pin.OUT)

        # Now to light up both of them using Pin class, you'll need to set
        # them to different values
        led1_pin.value(1)
        led2_pin.value(0)

        # Signal class allows to abstract away active-high/active-low
        # difference
        led1 = Signal(led1_pin, invert=False)
        led2 = Signal(led2_pin, invert=True)

        # Now lighting up them looks the same
        led1.value(1)
        led2.value(1)

        # Even better:
        led1.on()
        led2.on()

    Following is the guide when Signal vs Pin should be used:

    * Use Signal: If you want to control a simple on/off (including software
      PWM!) devices like LEDs, multi-segment indicators, relays, buzzers, or
      read simple binary sensors, like normally open or normally closed buttons,
      pulled high or low, Reed switches, moisture/flame detectors, etc. etc.
      Summing up, if you have a real physical device/sensor requiring GPIO
      access, you likely should use a Signal.

    * Use Pin: If you implement a higher-level protocol or bus to communicate
      with more complex devices.

    The split between Pin and Signal come from the use cases above and the
    architecture of MicroPython: Pin offers the lowest overhead, which may
    be important when bit-banging protocols. But Signal adds additional
    flexibility on top of Pin, at the cost of minor overhead (much smaller
    than if you implemented active-high vs active-low device differences in
    Python manually!). Also, Pin is a low-level object which needs to be
    implemented for each support board, while Signal is a high-level object
    which comes for free once Pin is implemented.

    If in doubt, give the Signal a try! Once again, it is offered to save
    developers from the need to handle unexciting differences like active-low
    vs active-high signals, and allow other users to share and enjoy your
    application, instead of being frustrated by the fact that it doesn't
    work for them simply because their LEDs or relays are wired in a slightly
    different way.
    """

    def off(self) -> None:
        """
        Deactivate signal.
        """
        ...

    def on(self) -> None:
        """
        Activate signal.
        """
        ...

    @overload
    def value(self) -> int:
        """
        This method allows to set and get the value of the signal, depending on whether
        the argument ``x`` is supplied or not.

        If the argument is omitted then this method gets the signal level, 1 meaning
        signal is asserted (active) and 0 - signal inactive.

        If the argument is supplied then this method sets the signal level. The
        argument ``x`` can be anything that converts to a boolean. If it converts
        to ``True``, the signal is active, otherwise it is inactive.

        Correspondence between signal being active and actual logic level on the
        underlying pin depends on whether signal is inverted (active-low) or not.
        For non-inverted signal, active status corresponds to logical 1, inactive -
        to logical 0. For inverted/active-low signal, active status corresponds
        to logical 0, while inactive - to logical 1.
        """

    @overload
    def value(self, x: Any, /) -> None:
        """
        This method allows to set and get the value of the signal, depending on whether
        the argument ``x`` is supplied or not.

        If the argument is omitted then this method gets the signal level, 1 meaning
        signal is asserted (active) and 0 - signal inactive.

        If the argument is supplied then this method sets the signal level. The
        argument ``x`` can be anything that converts to a boolean. If it converts
        to ``True``, the signal is active, otherwise it is inactive.

        Correspondence between signal being active and actual logic level on the
        underlying pin depends on whether signal is inverted (active-low) or not.
        For non-inverted signal, active status corresponds to logical 1, inactive -
        to logical 0. For inverted/active-low signal, active status corresponds
        to logical 0, while inactive - to logical 1.
        """

    @overload
    def __init__(self, pin_obj: PinLike, invert: bool = False, /):
        """
        Create a Signal object. There're two ways to create it:

        * By wrapping existing Pin object - universal method which works for
          any board.
        * By passing required Pin parameters directly to Signal constructor,
          skipping the need to create intermediate Pin object. Available on
          many, but not all boards.

        The arguments are:

          - ``pin_obj`` is existing Pin object.

          - ``pin_arguments`` are the same arguments as can be passed to Pin constructor.

          - ``invert`` - if True, the signal will be inverted (active low).
        """

    @overload
    def __init__(
        self,
        id: PinLike,
        /,
        mode: int = -1,
        pull: int = -1,
        *,
        value: Any = None,
        drive: int | None = None,
        alt: int | None = None,
        invert: bool = False,
    ):
        """
        Create a Signal object. There're two ways to create it:

        * By wrapping existing Pin object - universal method which works for
          any board.
        * By passing required Pin parameters directly to Signal constructor,
          skipping the need to create intermediate Pin object. Available on
          many, but not all boards.

        The arguments are:

          - ``pin_obj`` is existing Pin object.

          - ``pin_arguments`` are the same arguments as can be passed to Pin constructor.

          - ``invert`` - if True, the signal will be inverted (active low).
        """
