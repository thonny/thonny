"""
Functions related to the board.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/pyb.html

The ``pyb`` module contains specific functions related to the board.

---
Module: 'pyb' on micropython-v1.25.0-stm32-PYBV11
"""

# MCU: {'version': '1.25.0', 'mpy': 'v6.3', 'port': 'stm32', 'board': 'PYBV11', 'family': 'micropython', 'build': '', 'arch': 'armv7emsp', 'ver': '1.25.0', 'cpu': 'STM32F405RG'}
# Stubber: v1.24.0
from __future__ import annotations
from typing import NoReturn, Any, Dict, List, Callable, overload, Tuple, Final
from _typeshed import Incomplete
from typing_extensions import deprecated, Awaitable, TypeAlias, TypeVar
from _mpy_shed import HID_Tuple, _OldAbstractBlockDev, _OldAbstractReadOnlyBlockDev, AnyReadableBuf, AnyWritableBuf
from collections.abc import Sequence
from vfs import AbstractBlockDev
from array import array
from abc import ABC, abstractmethod

hid_mouse: tuple = ()
hid_keyboard: tuple = ()

def hard_reset() -> NoReturn:
    """
    Resets the pyboard in a manner similar to pushing the external RESET
    button.
    """
    ...

@deprecated("Use `pyb.USB_VCP().isconnected()` instead.")
def have_cdc() -> bool:
    """
    Return True if USB is connected as a serial device, False otherwise.

    ``Note:`` This function is deprecated.  Use pyb.USB_VCP().isconnected() instead.
    """
    ...

@deprecated("Use `pyb.USB_HID.send()`` instead.")
@overload
def hid(data: tuple[int, int, int, int], /) -> None:
    """
    Takes a 4-tuple (or list) and sends it to the USB host (the PC) to
    signal a HID mouse-motion event.

    ``Note:`` This function is deprecated.  Use :meth:`pyb.USB_HID.send()` instead.
    """

@deprecated("Use `pyb.USB_HID.send()`` instead.")
@overload
def hid(data: Sequence[int], /) -> None:
    """
    Takes a 4-tuple (or list) and sends it to the USB host (the PC) to
    signal a HID mouse-motion event.

    ``Note:`` This function is deprecated.  Use :meth:`pyb.USB_HID.send()` instead.
    """

@overload
def info() -> None:
    """
    Print out lots of information about the board.
    """

@overload
def info(dump_alloc_table: bytes, /) -> None:
    """
    Print out lots of information about the board.
    """

@overload
def info(self) -> list[int]:
    """
    Print out lots of information about the board.
    """

@overload
def info(self, list: list[int], /) -> list[int]:
    """
    Print out lots of information about the board.
    """

def wfi() -> None:
    """
    Wait for an internal or external interrupt.

    This executes a ``wfi`` instruction which reduces power consumption
    of the MCU until any interrupt occurs (be it internal or external),
    at which point execution continues.  Note that the system-tick interrupt
    occurs once every millisecond (1000Hz) so this function will block for
    at most 1ms.
    """
    ...

def elapsed_micros(start: int, /) -> int:
    """
    Returns the number of microseconds which have elapsed since ``start``.

    This function takes care of counter wrap, and always returns a positive
    number. This means it can be used to measure periods up to about 17.8 minutes.

    Example::

        start = pyb.micros()
        while pyb.elapsed_micros(start) < 1000:
            # Perform some operation
            pass
    """
    ...

@overload
def freq() -> tuple[int, int, int, int]:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

@overload
def freq(sysclk: int, /) -> None:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

@overload
def freq(sysclk: int, hclk: int, /) -> None:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

@overload
def freq(sysclk: int, hclk: int, pclk1: int, /) -> None:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

@overload
def freq(sysclk: int, hclk: int, pclk1: int, pclk2: int, /) -> None:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

@overload
def freq(self) -> int:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

@overload
def freq(self, value: int, /) -> None:
    """
    If given no arguments, returns a tuple of clock frequencies:
    (sysclk, hclk, pclk1, pclk2).
    These correspond to:

     - sysclk: frequency of the CPU
     - hclk: frequency of the AHB bus, core memory and DMA
     - pclk1: frequency of the APB1 bus
     - pclk2: frequency of the APB2 bus

    If given any arguments then the function sets the frequency of the CPU,
    and the buses if additional arguments are given.  Frequencies are given in
    Hz.  Eg freq(120000000) sets sysclk (the CPU frequency) to 120MHz.  Note that
    not all values are supported and the largest supported frequency not greater
    than the given value will be selected.

    Supported sysclk frequencies are (in MHz): 8, 16, 24, 30, 32, 36, 40, 42, 48,
    54, 56, 60, 64, 72, 84, 96, 108, 120, 144, 168.

    The maximum frequency of hclk is 168MHz, of pclk1 is 42MHz, and of pclk2 is
    84MHz.  Be sure not to set frequencies above these values.

    The hclk, pclk1 and pclk2 frequencies are derived from the sysclk frequency
    using a prescaler (divider).  Supported prescalers for hclk are: 1, 2, 4, 8,
    16, 64, 128, 256, 512.  Supported prescalers for pclk1 and pclk2 are: 1, 2,
    4, 8.  A prescaler will be chosen to best match the requested frequency.

    A sysclk frequency of
    8MHz uses the HSE (external crystal) directly and 16MHz uses the HSI
    (internal oscillator) directly.  The higher frequencies use the HSE to
    drive the PLL (phase locked loop), and then use the output of the PLL.

    Note that if you change the frequency while the USB is enabled then the USB
    may become unreliable. It is best to change the frequency in :ref:`boot.py`,
    before the USB peripheral is started. Also note that sysclk frequencies below
    36MHz do not allow the USB to function correctly.
    """

def disable_irq() -> bool:
    """
    Disable interrupt requests.
    Returns the previous IRQ state: ``False``/``True`` for disabled/enabled IRQs
    respectively.  This return value can be passed to enable_irq to restore
    the IRQ to its original state.
    """
    ...

def fault_debug(value: bool = False) -> None:
    """
    Enable or disable hard-fault debugging.  A hard-fault is when there is a fatal
    error in the underlying system, like an invalid memory access.

    If the *value* argument is ``False`` then the board will automatically reset if
    there is a hard fault.

    If *value* is ``True`` then, when the board has a hard fault, it will print the
    registers and the stack trace, and then cycle the LEDs indefinitely.

    The default value is disabled, i.e. to automatically reset.
    """
    ...

def elapsed_millis(start: int, /) -> int:
    """
    Returns the number of milliseconds which have elapsed since ``start``.

    This function takes care of counter wrap, and always returns a positive
    number. This means it can be used to measure periods up to about 12.4 days.

    Example::

        start = pyb.millis()
        while pyb.elapsed_millis(start) < 1000:
            # Perform some operation
    """
    ...

def enable_irq(state: bool = True, /) -> None:
    """
    Enable interrupt requests.
    If ``state`` is ``True`` (the default value) then IRQs are enabled.
    If ``state`` is ``False`` then IRQs are disabled.  The most common use of
    this function is to pass it the value returned by ``disable_irq`` to
    exit a critical section.
    """
    ...

def sync() -> None:
    """
    Sync all file systems.
    """
    ...

def servo(*args, **kwargs) -> Incomplete: ...
def standby() -> None:
    """
    Put the pyboard into a "deep sleep" state.

    This reduces power consumption to less than 50 uA.  To wake from this
    sleep state requires a real-time-clock event, or an external interrupt
    on X1 (PA0=WKUP) or X18 (PC13=TAMP1).
    Upon waking the system undergoes a hard reset.

    See :meth:`rtc.wakeup` to configure a real-time-clock wakeup event.
    """
    ...

# noinspection PyShadowingNames
@overload
def usb_mode() -> str:
    """
    If called with no arguments, return the current USB mode as a string.

    If called with *modestr* provided, attempts to configure the USB mode.
    The following values of *modestr* are understood:

    - ``None``: disables USB
    - ``'VCP'``: enable with VCP (Virtual COM Port) interface
    - ``'MSC'``: enable with MSC (mass storage device class) interface
    - ``'VCP+MSC'``: enable with VCP and MSC
    - ``'VCP+HID'``: enable with VCP and HID (human interface device)
    - ``'VCP+MSC+HID'``: enabled with VCP, MSC and HID (only available on PYBD boards)

    For backwards compatibility, ``'CDC'`` is understood to mean
    ``'VCP'`` (and similarly for ``'CDC+MSC'`` and ``'CDC+HID'``).

    The *port* parameter should be an integer (0, 1, ...) and selects which
    USB port to use if the board supports multiple ports.  A value of -1 uses
    the default or automatically selected port.

    The *vid* and *pid* parameters allow you to specify the VID (vendor id)
    and PID (product id).  A *pid* value of -1 will select a PID based on the
    value of *modestr*.

    If enabling MSC mode, the *msc* parameter can be used to specify a list
    of SCSI LUNs to expose on the mass storage interface.  For example
    ``msc=(pyb.Flash(), pyb.SDCard())``.

    If enabling HID mode, you may also specify the HID details by
    passing the *hid* keyword parameter.  It takes a tuple of
    (subclass, protocol, max packet length, polling interval, report
    descriptor).  By default it will set appropriate values for a USB
    mouse.  There is also a ``pyb.hid_keyboard`` constant, which is an
    appropriate tuple for a USB keyboard.

    The *high_speed* parameter, when set to ``True``, enables USB HS mode if
    it is supported by the hardware.
    """

# noinspection PyShadowingNames
@overload
def usb_mode(
    modestr: str,
    /,
    *,
    port: int = -1,
    vid: int = 0xF055,
    pid: int = -1,
    msc: Sequence[AbstractBlockDev] = (),
    hid: tuple[int, int, int, int, bytes] = hid_mouse,
    high_speed: bool = False,
) -> None:
    """
    If called with no arguments, return the current USB mode as a string.

    If called with *modestr* provided, attempts to configure the USB mode.
    The following values of *modestr* are understood:

    - ``None``: disables USB
    - ``'VCP'``: enable with VCP (Virtual COM Port) interface
    - ``'MSC'``: enable with MSC (mass storage device class) interface
    - ``'VCP+MSC'``: enable with VCP and MSC
    - ``'VCP+HID'``: enable with VCP and HID (human interface device)
    - ``'VCP+MSC+HID'``: enabled with VCP, MSC and HID (only available on PYBD boards)

    For backwards compatibility, ``'CDC'`` is understood to mean
    ``'VCP'`` (and similarly for ``'CDC+MSC'`` and ``'CDC+HID'``).

    The *port* parameter should be an integer (0, 1, ...) and selects which
    USB port to use if the board supports multiple ports.  A value of -1 uses
    the default or automatically selected port.

    The *vid* and *pid* parameters allow you to specify the VID (vendor id)
    and PID (product id).  A *pid* value of -1 will select a PID based on the
    value of *modestr*.

    If enabling MSC mode, the *msc* parameter can be used to specify a list
    of SCSI LUNs to expose on the mass storage interface.  For example
    ``msc=(pyb.Flash(), pyb.SDCard())``.

    If enabling HID mode, you may also specify the HID details by
    passing the *hid* keyword parameter.  It takes a tuple of
    (subclass, protocol, max packet length, polling interval, report
    descriptor).  By default it will set appropriate values for a USB
    mouse.  There is also a ``pyb.hid_keyboard`` constant, which is an
    appropriate tuple for a USB keyboard.

    The *high_speed* parameter, when set to ``True``, enables USB HS mode if
    it is supported by the hardware.
    """

def udelay(us: int, /) -> None:
    """
    Delay for the given number of microseconds.
    """
    ...

def unique_id() -> str:
    """
    Returns a string of 12 bytes (96 bits), which is the unique ID of the MCU.
    """
    ...

def micros() -> int:
    """
    Returns the number of microseconds since the board was last reset.

    The result is always a MicroPython smallint (31-bit signed number), so
    after 2^30 microseconds (about 17.8 minutes) this will start to return
    negative numbers.

    Note that if :meth:`pyb.stop()` is issued the hardware counter supporting this
    function will pause for the duration of the "sleeping" state. This
    will affect the outcome of :meth:`pyb.elapsed_micros()`.
    """
    ...

@overload
def mount(
    device: _OldAbstractReadOnlyBlockDev,
    mountpoint: str,
    /,
    *,
    readonly: bool = False,
    mkfs: bool = False,
) -> None:
    """
    ``Note:`` This function is deprecated. Mounting and unmounting devices should
       be performed by :meth:`vfs.mount` and :meth:`vfs.umount` instead.

    Mount a block device and make it available as part of the filesystem.
    ``device`` must be an object that provides the block protocol. (The
    following is also deprecated. See :class:`vfs.AbstractBlockDev` for the
    correct way to create a block device.)

     - ``readblocks(self, blocknum, buf)``
     - ``writeblocks(self, blocknum, buf)`` (optional)
     - ``count(self)``
     - ``sync(self)`` (optional)

    ``readblocks`` and ``writeblocks`` should copy data between ``buf`` and
    the block device, starting from block number ``blocknum`` on the device.
    ``buf`` will be a bytearray with length a multiple of 512.  If
    ``writeblocks`` is not defined then the device is mounted read-only.
    The return value of these two functions is ignored.

    ``count`` should return the number of blocks available on the device.
    ``sync``, if implemented, should sync the data on the device.

    The parameter ``mountpoint`` is the location in the root of the filesystem
    to mount the device.  It must begin with a forward-slash.

    If ``readonly`` is ``True``, then the device is mounted read-only,
    otherwise it is mounted read-write.

    If ``mkfs`` is ``True``, then a new filesystem is created if one does not
    already exist.
    """

@overload
def mount(
    device: _OldAbstractBlockDev,
    mountpoint: str,
    /,
    *,
    readonly: bool = False,
    mkfs: bool = False,
) -> None:
    """
    ``Note:`` This function is deprecated. Mounting and unmounting devices should
       be performed by :meth:`vfs.mount` and :meth:`vfs.umount` instead.

    Mount a block device and make it available as part of the filesystem.
    ``device`` must be an object that provides the block protocol. (The
    following is also deprecated. See :class:`vfs.AbstractBlockDev` for the
    correct way to create a block device.)

     - ``readblocks(self, blocknum, buf)``
     - ``writeblocks(self, blocknum, buf)`` (optional)
     - ``count(self)``
     - ``sync(self)`` (optional)

    ``readblocks`` and ``writeblocks`` should copy data between ``buf`` and
    the block device, starting from block number ``blocknum`` on the device.
    ``buf`` will be a bytearray with length a multiple of 512.  If
    ``writeblocks`` is not defined then the device is mounted read-only.
    The return value of these two functions is ignored.

    ``count`` should return the number of blocks available on the device.
    ``sync``, if implemented, should sync the data on the device.

    The parameter ``mountpoint`` is the location in the root of the filesystem
    to mount the device.  It must begin with a forward-slash.

    If ``readonly`` is ``True``, then the device is mounted read-only,
    otherwise it is mounted read-write.

    If ``mkfs`` is ``True``, then a new filesystem is created if one does not
    already exist.
    """

def rng() -> int:
    """
    Return a 30-bit hardware generated random number.
    """
    ...

def millis() -> int:
    """
    Returns the number of milliseconds since the board was last reset.

    The result is always a MicroPython smallint (31-bit signed number), so
    after 2^30 milliseconds (about 12.4 days) this will start to return
    negative numbers.

    Note that if :meth:`pyb.stop()` is issued the hardware counter supporting this
    function will pause for the duration of the "sleeping" state. This
    will affect the outcome of :meth:`pyb.elapsed_millis()`.
    """
    ...

@overload
def repl_uart() -> UART | None:
    """
    Get or set the UART object where the REPL is repeated on.
    """

@overload
def repl_uart(uart: UART, /) -> None:
    """
    Get or set the UART object where the REPL is repeated on.
    """

def pwm(*args, **kwargs) -> Incomplete: ...
def repl_info(*args, **kwargs) -> Incomplete: ...
def stop() -> None:
    """
    Put the pyboard in a "sleeping" state.

    This reduces power consumption to less than 500 uA.  To wake from this
    sleep state requires an external interrupt or a real-time-clock event.
    Upon waking execution continues where it left off.

    See :meth:`rtc.wakeup` to configure a real-time-clock wakeup event.
    """
    ...

def delay(ms: int, /) -> None:
    """
    Delay for the given number of milliseconds.
    """
    ...

def main(filename: str, /) -> None:
    """
    Set the filename of the main script to run after :ref:`boot.py` is finished.
    If this function is not called then the default file :ref:`main.py` will be
    executed.

    It only makes sense to call this function from within boot.py.
    """
    ...

def bootloader() -> None:
    """
    Activate the bootloader without BOOT* pins.
    """
    ...

def country(*args, **kwargs) -> Incomplete: ...

class DAC:
    """
    The DAC is used to output analog values (a specific voltage) on pin X5 or pin X6.
    The voltage will be between 0 and 3.3V.

    *This module will undergo changes to the API.*

    Example usage::

        from pyb import DAC

        dac = DAC(1)            # create DAC 1 on pin X5
        dac.write(128)          # write a value to the DAC (makes X5 1.65V)

        dac = DAC(1, bits=12)   # use 12 bit resolution
        dac.write(4095)         # output maximum value, 3.3V

    To output a continuous sine-wave::

        import math
        from pyb import DAC

        # create a buffer containing a sine-wave
        buf = bytearray(100)
        for i in range(len(buf)):
            buf[i] = 128 + int(127 * math.sin(2 * math.pi * i / len(buf)))

        # output the sine-wave at 400Hz
        dac = DAC(1)
        dac.write_timed(buf, 400 * len(buf), mode=DAC.CIRCULAR)

    To output a continuous sine-wave at 12-bit resolution::

        import math
        from array import array
        from pyb import DAC

        # create a buffer containing a sine-wave, using half-word samples
        buf = array('H', 2048 + int(2047 * math.sin(2 * math.pi * i / 128)) for i in range(128))

        # output the sine-wave at 400Hz
        dac = DAC(1, bits=12)
        dac.write_timed(buf, 400 * len(buf), mode=DAC.CIRCULAR)
    """

    CIRCULAR: Final[int] = 256
    NORMAL: Final[int] = 0
    def noise(self, freq: int, /) -> None:
        """
        Generate a pseudo-random noise signal.  A new random sample is written
        to the DAC output at the given frequency.
        """
        ...

    def write_timed(self, data: AnyWritableBuf, freq: int | Timer, /, *, mode: int = NORMAL) -> None:
        """
        Initiates a burst of RAM to DAC using a DMA transfer.
        The input data is treated as an array of bytes in 8-bit mode, and
        an array of unsigned half-words (array typecode 'H') in 12-bit mode.

        ``freq`` can be an integer specifying the frequency to write the DAC
        samples at, using Timer(6).  Or it can be an already-initialised
        Timer object which is used to trigger the DAC sample.  Valid timers
        are 2, 4, 5, 6, 7 and 8.

        ``mode`` can be ``DAC.NORMAL`` or ``DAC.CIRCULAR``.

        Example using both DACs at the same time::

          dac1 = DAC(1)
          dac2 = DAC(2)
          dac1.write_timed(buf1, pyb.Timer(6, freq=100), mode=DAC.CIRCULAR)
          dac2.write_timed(buf2, pyb.Timer(7, freq=200), mode=DAC.CIRCULAR)
        """
        ...

    def triangle(self, freq: int, /) -> None:
        """
        Generate a triangle wave.  The value on the DAC output changes at the given
        frequency and ramps through the full 12-bit range (up and down). Therefore
        the frequency of the repeating triangle wave itself is 8192 times smaller.
        """
        ...

    def write(self, value: int, /) -> None:
        """
        Direct access to the DAC output.  The minimum value is 0.  The maximum
        value is 2**``bits``-1, where ``bits`` is set when creating the DAC
        object or by using the ``init`` method.
        """
        ...

    def init(self, bits: int = 8, *, buffering: bool | None = None) -> None:
        """
        Reinitialise the DAC.  *bits* can be 8 or 12.  *buffering* can be
        ``None``, ``False`` or ``True``; see above constructor for the meaning
        of this parameter.
        """
        ...

    def deinit(self) -> None:
        """
        De-initialise the DAC making its pin available for other uses.
        """
        ...

    def __init__(self, port: int | Pin, /, bits: int = 8, *, buffering: bool | None = None) -> None:
        """
        Construct a new DAC object.

        ``port`` can be a pin object, or an integer (1 or 2).
        DAC(1) is on pin X5 and DAC(2) is on pin X6.

        ``bits`` is an integer specifying the resolution, and can be 8 or 12.
        The maximum value for the write and write_timed methods will be
        2\*\*``bits``-1.

        The *buffering* parameter selects the behaviour of the DAC op-amp output
        buffer, whose purpose is to reduce the output impedance.  It can be
        ``None`` to select the default (buffering enabled for :meth:`DAC.noise`,
        :meth:`DAC.triangle` and :meth:`DAC.write_timed`, and disabled for
        :meth:`DAC.write`), ``False`` to disable buffering completely, or ``True``
        to enable output buffering.

        When buffering is enabled the DAC pin can drive loads down to 5KΩ.
        Otherwise it has an output impedance of 15KΩ maximum: consequently
        to achieve a 1% accuracy without buffering requires the applied load
        to be less than 1.5MΩ.  Using the buffer incurs a penalty in accuracy,
        especially near the extremes of range.
        """

class ExtInt:
    """
    There are a total of 22 interrupt lines. 16 of these can come from GPIO pins
    and the remaining 6 are from internal sources.

    For lines 0 through 15, a given line can map to the corresponding line from an
    arbitrary port. So line 0 can map to Px0 where x is A, B, C, ... and
    line 1 can map to Px1 where x is A, B, C, ... ::

        def callback(line):
            print("line =", line)

    Note: ExtInt will automatically configure the gpio line as an input. ::

        extint = pyb.ExtInt(pin, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, callback)

    Now every time a falling edge is seen on the X1 pin, the callback will be
    called. Caution: mechanical pushbuttons have "bounce" and pushing or
    releasing a switch will often generate multiple edges.
    See: http://www.eng.utah.edu/~cs5780/debouncing.pdf for a detailed
    explanation, along with various techniques for debouncing.

    Trying to register 2 callbacks onto the same pin will throw an exception.

    If pin is passed as an integer, then it is assumed to map to one of the
    internal interrupt sources, and must be in the range 16 through 22.

    All other pin objects go through the pin mapper to come up with one of the
    gpio pins. ::

        extint = pyb.ExtInt(pin, mode, pull, callback)

    Valid modes are pyb.ExtInt.IRQ_RISING, pyb.ExtInt.IRQ_FALLING,
    pyb.ExtInt.IRQ_RISING_FALLING, pyb.ExtInt.EVT_RISING,
    pyb.ExtInt.EVT_FALLING, and pyb.ExtInt.EVT_RISING_FALLING.

    Only the IRQ_xxx modes have been tested. The EVT_xxx modes have
    something to do with sleep mode and the WFE instruction.

    Valid pull values are pyb.Pin.PULL_UP, pyb.Pin.PULL_DOWN, pyb.Pin.PULL_NONE.

    There is also a C API, so that drivers which require EXTI interrupt lines
    can also use this code. See extint.h for the available functions and
    usrsw.h for an example of using this.
    """

    IRQ_FALLING: Final[int] = 270598144
    IRQ_RISING_FALLING: Final[int] = 271646720
    IRQ_RISING: Final[int] = 269549568
    EVT_FALLING: Final[int] = 270663680
    EVT_RISING_FALLING: Final[int] = 271712256
    EVT_RISING: Final[int] = 269615104
    def line(self) -> int:
        """
        Return the line number that the pin is mapped to.
        """
        ...

    @staticmethod
    def regs() -> None:
        """
        Dump the values of the EXTI registers.
        """
        ...

    def swint(self) -> None:
        """
        Trigger the callback from software.
        """
        ...

    def enable(self) -> None:
        """
        Enable a disabled interrupt.
        """
        ...

    def disable(self) -> None:
        """
        Disable the interrupt associated with the ExtInt object.
        This could be useful for debouncing.
        """
        ...

    def __init__(
        self,
        pin: int | str | Pin,
        mode: int,
        pull: int,
        callback: Callable[[int], None],
    ) -> None:
        """
        Create an ExtInt object:

          - ``pin`` is the pin on which to enable the interrupt (can be a pin object or any valid pin name).
          - ``mode`` can be one of:
            - ``ExtInt.IRQ_RISING`` - trigger on a rising edge;
            - ``ExtInt.IRQ_FALLING`` - trigger on a falling edge;
            - ``ExtInt.IRQ_RISING_FALLING`` - trigger on a rising or falling edge.
          - ``pull`` can be one of:
            - ``pyb.Pin.PULL_NONE`` - no pull up or down resistors;
            - ``pyb.Pin.PULL_UP`` - enable the pull-up resistor;
            - ``pyb.Pin.PULL_DOWN`` - enable the pull-down resistor.
          - ``callback`` is the function to call when the interrupt triggers.  The
            callback function must accept exactly 1 argument, which is the line that
            triggered the interrupt.
        """

class Flash(AbstractBlockDev):
    """
    The Flash class allows direct access to the primary flash device on the pyboard.

    In most cases, to store persistent data on the device, you'll want to use a
    higher-level abstraction, for example the filesystem via Python's standard file
    API, but this interface is useful to :ref:`customise the filesystem
    configuration <filesystem>` or implement a low-level storage system for your
    application.
    """

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

    def ioctl(self, op: int, arg: int) -> int | None:
        """
        These methods implement the simple and :ref:`extended
        <block-device-interface>` block protocol defined by
        :class:`vfs.AbstractBlockDev`.
        """
        ...

    @deprecated("This constructor is deprecated and will be removed in a future version of MicroPython")
    @overload
    def __init__(self):
        """
        Create and return a block device that represents the flash device presented
        to the USB mass storage interface.

        It includes a virtual partition table at the start, and the actual flash
        starts at block ``0x100``.

        This constructor is deprecated and will be removed in a future version of MicroPython.
        """

    @overload
    def __init__(self, *, start: int = -1, len: int = -1):
        """
        Create and return a block device that accesses the flash at the specified offset. The length defaults to the remaining size of the device.

        The *start* and *len* offsets are in bytes, and must be a multiple of the block size (typically 512 for internal flash).
        """

class I2C:
    """
    I2C is a two-wire protocol for communicating between devices.  At the physical
    level it consists of 2 wires: SCL and SDA, the clock and data lines respectively.

    I2C objects are created attached to a specific bus.  They can be initialised
    when created, or initialised later on.

    Example::

        from pyb import I2C

        i2c = I2C(1)                             # create on bus 1
        i2c = I2C(1, I2C.CONTROLLER)             # create and init as a controller
        i2c.init(I2C.CONTROLLER, baudrate=20000) # init as a controller
        i2c.init(I2C.PERIPHERAL, addr=0x42)      # init as a peripheral with given address
        i2c.deinit()                             # turn off the I2C unit

    Printing the i2c object gives you information about its configuration.

    The basic methods are send and recv::

        i2c.send('abc')      # send 3 bytes
        i2c.send(0x42)       # send a single byte, given by the number
        data = i2c.recv(3)   # receive 3 bytes

    To receive inplace, first create a bytearray::

        data = bytearray(3)  # create a buffer
        i2c.recv(data)       # receive 3 bytes, writing them into data

    You can specify a timeout (in ms)::

        i2c.send(b'123', timeout=2000)   # timeout after 2 seconds

    A controller must specify the recipient's address::

        i2c.init(I2C.CONTROLLER)
        i2c.send('123', 0x42)        # send 3 bytes to peripheral with address 0x42
        i2c.send(b'456', addr=0x42)  # keyword for address

    Master also has other methods::

        i2c.is_ready(0x42)           # check if peripheral 0x42 is ready
        i2c.scan()                   # scan for peripherals on the bus, returning
                                     #   a list of valid addresses
        i2c.mem_read(3, 0x42, 2)     # read 3 bytes from memory of peripheral 0x42,
                                     #   starting at address 2 in the peripheral
        i2c.mem_write('abc', 0x42, 2, timeout=1000) # write 'abc' (3 bytes) to memory of peripheral 0x42
                                                    # starting at address 2 in the peripheral, timeout after 1 second
    """

    PERIPHERAL: Final[int] = 1
    MASTER: Final[int] = 0
    CONTROLLER: Final[int] = 0
    SLAVE: Final[int] = 1
    def scan(self) -> List:
        """
        Scan all I2C addresses from 0x01 to 0x7f and return a list of those that respond.
        Only valid when in controller mode.
        """
        ...

    @overload
    def mem_read(
        self,
        data: int,
        addr: int,
        memaddr: int,
        /,
        *,
        timeout: int = 5000,
        addr_size: int = 8,
    ) -> bytes:
        """
        Read from the memory of an I2C device:

          - ``data`` can be an integer (number of bytes to read) or a buffer to read into
          - ``addr`` is the I2C device address
          - ``memaddr`` is the memory location within the I2C device
          - ``timeout`` is the timeout in milliseconds to wait for the read
          - ``addr_size`` selects width of memaddr: 8 or 16 bits

        Returns the read data.
        This is only valid in controller mode.
        """

    @overload
    def mem_read(
        self,
        data: AnyWritableBuf,
        addr: int,
        memaddr: int,
        /,
        *,
        timeout: int = 5000,
        addr_size: int = 8,
    ) -> AnyWritableBuf:
        """
        Read from the memory of an I2C device:

          - ``data`` can be an integer (number of bytes to read) or a buffer to read into
          - ``addr`` is the I2C device address
          - ``memaddr`` is the memory location within the I2C device
          - ``timeout`` is the timeout in milliseconds to wait for the read
          - ``addr_size`` selects width of memaddr: 8 or 16 bits

        Returns the read data.
        This is only valid in controller mode.
        """

    def mem_write(
        self,
        data: int | AnyWritableBuf,
        addr: int,
        memaddr: int,
        /,
        *,
        timeout: int = 5000,
        addr_size: int = 8,
    ) -> None:
        """
        Write to the memory of an I2C device:

          - ``data`` can be an integer or a buffer to write from
          - ``addr`` is the I2C device address
          - ``memaddr`` is the memory location within the I2C device
          - ``timeout`` is the timeout in milliseconds to wait for the write
          - ``addr_size`` selects width of memaddr: 8 or 16 bits

        Returns ``None``.
        This is only valid in controller mode.
        """
        ...

    @overload
    def recv(
        self,
        recv: int,
        addr: int = 0x00,
        /,
        *,
        timeout: int = 5000,
    ) -> bytes:
        """
        Receive data on the bus:

          - ``recv`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes
          - ``addr`` is the address to receive from (only required in controller mode)
          - ``timeout`` is the timeout in milliseconds to wait for the receive

        Return value: if ``recv`` is an integer then a new buffer of the bytes received,
        otherwise the same buffer that was passed in to ``recv``.
        """

    @overload
    def recv(
        self,
        recv: AnyWritableBuf,
        addr: int = 0x00,
        /,
        *,
        timeout: int = 5000,
    ) -> AnyWritableBuf:
        """
        Receive data on the bus:

          - ``recv`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes
          - ``addr`` is the address to receive from (only required in controller mode)
          - ``timeout`` is the timeout in milliseconds to wait for the receive

        Return value: if ``recv`` is an integer then a new buffer of the bytes received,
        otherwise the same buffer that was passed in to ``recv``.
        """

    def is_ready(self, addr: int, /) -> bool:
        """
        Check if an I2C device responds to the given address.  Only valid when in controller mode.
        """
        ...

    def send(
        self,
        addr: int = 0x00,
        /,
        *,
        timeout: int = 5000,
    ) -> None:
        """
        Send data on the bus:

          - ``send`` is the data to send (an integer to send, or a buffer object)
          - ``addr`` is the address to send to (only required in controller mode)
          - ``timeout`` is the timeout in milliseconds to wait for the send

        Return value: ``None``.
        """
        ...

    def deinit(self) -> None:
        """
        Turn off the I2C bus.
        """
        ...

    def init(
        self,
        bus: int | str,
        mode: str,
        /,
        *,
        addr: int = 0x12,
        baudrate: int = 400_000,
        gencall: bool = False,
        dma: bool = False,
    ) -> None:
        """
        Initialise the I2C bus with the given parameters:

           - ``mode`` must be either ``I2C.CONTROLLER`` or ``I2C.PERIPHERAL``
           - ``addr`` is the 7-bit address (only sensible for a peripheral)
           - ``baudrate`` is the SCL clock rate (only sensible for a controller)
           - ``gencall`` is whether to support general call mode
           - ``dma`` is whether to allow the use of DMA for the I2C transfers (note
             that DMA transfers have more precise timing but currently do not handle bus
             errors properly)

         The actual clock frequency may be lower than the requested frequency.
         This is dependent on the platform hardware. The actual rate may be determined
         by printing the I2C object.
        """
        ...

    def __init__(
        self,
        bus: int | str,
        mode: str,
        /,
        *,
        addr: int = 0x12,
        baudrate: int = 400_000,
        gencall: bool = False,
        dma: bool = False,
    ) -> None:
        """
        Construct an I2C object on the given bus.  ``bus`` can be 1 or 2, 'X' or
        'Y'. With no additional parameters, the I2C object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.

        The physical pins of the I2C buses on Pyboards V1.0 and V1.1 are:

          - ``I2C(1)`` is on the X position: ``(SCL, SDA) = (X9, X10) = (PB6, PB7)``
          - ``I2C(2)`` is on the Y position: ``(SCL, SDA) = (Y9, Y10) = (PB10, PB11)``

        On the Pyboard Lite:

          - ``I2C(1)`` is on the X position: ``(SCL, SDA) = (X9, X10) = (PB6, PB7)``
          - ``I2C(3)`` is on the Y position: ``(SCL, SDA) = (Y9, Y10) = (PA8, PB8)``

        Calling the constructor with 'X' or 'Y' enables portability between Pyboard
        types.
        """

class LCD:
    """
    The LCD class is used to control the LCD on the LCD touch-sensor pyskin,
    LCD32MKv1.0.  The LCD is a 128x32 pixel monochrome screen, part NHD-C12832A1Z.

    The pyskin must be connected in either the X or Y positions, and then
    an LCD object is made using::

        lcd = pyb.LCD('X')      # if pyskin is in the X position
        lcd = pyb.LCD('Y')      # if pyskin is in the Y position

    Then you can use::

        lcd.light(True)                 # turn the backlight on
        lcd.write('Hello world!\n')     # print text to the screen

    This driver implements a double buffer for setting/getting pixels.
    For example, to make a bouncing dot, try::

        x = y = 0
        dx = dy = 1
        while True:
            # update the dot's position
            x += dx
            y += dy

            # make the dot bounce of the edges of the screen
            if x <= 0 or x >= 127: dx = -dx
            if y <= 0 or y >= 31: dy = -dy

            lcd.fill(0)                 # clear the buffer
            lcd.pixel(x, y, 1)          # draw the dot
            lcd.show()                  # show the buffer
            pyb.delay(50)               # pause for 50ms
    """

    def fill(self, colour: int, /) -> None:
        """
        Fill the screen with the given colour (0 or 1 for white or black).

        This method writes to the hidden buffer.  Use ``show()`` to show the buffer.
        """
        ...

    def light(self, value: bool | int, /) -> None:
        """
        Turn the backlight on/off.  True or 1 turns it on, False or 0 turns it off.
        """
        ...

    def pixel(self, x: int, y: int, colour: int, /) -> None:
        """
        Set the pixel at ``(x, y)`` to the given colour (0 or 1).

        This method writes to the hidden buffer.  Use ``show()`` to show the buffer.
        """
        ...

    def show(self) -> None:
        """
        Show the hidden buffer on the screen.
        """
        ...

    def text(self, str: str, x: int, y: int, colour: int, /) -> None:
        """
        Draw the given text to the position ``(x, y)`` using the given colour (0 or 1).

        This method writes to the hidden buffer.  Use ``show()`` to show the buffer.
        """
        ...

    def contrast(self, value: int, /) -> None:
        """
        Set the contrast of the LCD.  Valid values are between 0 and 47.
        """
        ...

    def get(self, x: int, y: int, /) -> int:
        """
        Get the pixel at the position ``(x, y)``.  Returns 0 or 1.

        This method reads from the visible buffer.
        """
        ...

    def write(self, str: str, /) -> None:
        """
        Write the string ``str`` to the screen.  It will appear immediately.
        """
        ...

    def command(self, inst_data: int, buf: bytes, /) -> None:
        """
        Send an arbitrary command to the LCD.  Pass 0 for ``instr_data`` to send an
        instruction, otherwise pass 1 to send data.  ``buf`` is a buffer with the
        instructions/data to send.
        """
        ...

    def __init__(self, skin_position: str, /) -> None:
        """
        Construct an LCD object in the given skin position.  ``skin_position`` can be 'X' or 'Y', and
        should match the position where the LCD pyskin is plugged in.
        """

class CAN:
    """
    CAN implements the standard CAN communications protocol.  At
    the physical level it consists of 2 lines: RX and TX.  Note that
    to connect the pyboard to a CAN bus you must use a CAN transceiver
    to convert the CAN logic signals from the pyboard to the correct
    voltage levels on the bus.

    Example usage (works without anything connected)::

        from pyb import CAN
        can = CAN(1, CAN.LOOPBACK)
        can.setfilter(0, CAN.LIST16, 0, (123, 124, 125, 126))  # set a filter to receive messages with id=123, 124, 125 and 126
        can.send('message!', 123)   # send a message with id 123
        can.recv(0)                 # receive message on FIFO 0
    """

    MASK16: Final[int] = 0
    MASK32: Final[int] = 2
    LOOPBACK: Final[int] = 67108864
    LIST32: Final[int] = 3
    SILENT_LOOPBACK: Final[int] = 201326592
    NORMAL: Final[int] = 0
    SILENT: Final[int] = 134217728
    STOPPED: Final[int] = 0
    ERROR_ACTIVE: Final[int] = 1
    BUS_OFF: Final[int] = 4
    LIST16: Final[int] = 1
    ERROR_PASSIVE: Final[int] = 3
    ERROR_WARNING: Final[int] = 2
    DUAL: Incomplete
    RANGE: Incomplete
    MASK: Incomplete
    def restart(self) -> None:
        """
        Force a software restart of the CAN controller without resetting its
        configuration.

        If the controller enters the bus-off state then it will no longer participate
        in bus activity.  If the controller is not configured to automatically restart
        (see :meth:`~CAN.init()`) then this method can be used to trigger a restart,
        and the controller will follow the CAN protocol to leave the bus-off state and
        go into the error active state.
        """
        ...

    @overload
    def recv(self, fifo: int, /, *, timeout: int = 5000) -> tuple[int, bool, int, memoryview]:
        """
        Receive data on the bus:

          - *fifo* is an integer, which is the FIFO to receive on
          - *list* is an optional list object to be used as the return value
          - *timeout* is the timeout in milliseconds to wait for the receive.

        Return value: A tuple containing five values.

          - The id of the message.
          - A boolean that indicates if the message ID is standard or extended.
          - A boolean that indicates if the message is an RTR message.
          - The FMI (Filter Match Index) value.
          - An array containing the data.

        If *list* is ``None`` then a new tuple will be allocated, as well as a new
        bytes object to contain the data (as the fifth element in the tuple).

        If *list* is not ``None`` then it should be a list object with a least five
        elements.  The fifth element should be a memoryview object which is created
        from either a bytearray or an array of type 'B' or 'b', and this array must
        have enough room for at least 8 bytes.  The list object will then be
        populated with the first four return values above, and the memoryview object
        will be resized inplace to the size of the data and filled in with that data.
        The same list and memoryview objects can be reused in subsequent calls to
        this method, providing a way of receiving data without using the heap.
        For example::

             buf = bytearray(8)
             lst = [0, 0, 0, 0, memoryview(buf)]
             # No heap memory is allocated in the following call
             can.recv(0, lst)
        """

    @overload
    def recv(self, fifo: int, list: None, /, *, timeout: int = 5000) -> tuple[int, bool, int, memoryview]:
        """
        Receive data on the bus:

          - *fifo* is an integer, which is the FIFO to receive on
          - *list* is an optional list object to be used as the return value
          - *timeout* is the timeout in milliseconds to wait for the receive.

        Return value: A tuple containing five values.

          - The id of the message.
          - A boolean that indicates if the message ID is standard or extended.
          - A boolean that indicates if the message is an RTR message.
          - The FMI (Filter Match Index) value.
          - An array containing the data.

        If *list* is ``None`` then a new tuple will be allocated, as well as a new
        bytes object to contain the data (as the fifth element in the tuple).

        If *list* is not ``None`` then it should be a list object with a least five
        elements.  The fifth element should be a memoryview object which is created
        from either a bytearray or an array of type 'B' or 'b', and this array must
        have enough room for at least 8 bytes.  The list object will then be
        populated with the first four return values above, and the memoryview object
        will be resized inplace to the size of the data and filled in with that data.
        The same list and memoryview objects can be reused in subsequent calls to
        this method, providing a way of receiving data without using the heap.
        For example::

             buf = bytearray(8)
             lst = [0, 0, 0, 0, memoryview(buf)]
             # No heap memory is allocated in the following call
             can.recv(0, lst)
        """

    @overload
    def recv(self, fifo: int, list: list[int | bool | memoryview], /, *, timeout: int = 5000) -> None:
        """
        Receive data on the bus:

          - *fifo* is an integer, which is the FIFO to receive on
          - *list* is an optional list object to be used as the return value
          - *timeout* is the timeout in milliseconds to wait for the receive.

        Return value: A tuple containing five values.

          - The id of the message.
          - A boolean that indicates if the message ID is standard or extended.
          - A boolean that indicates if the message is an RTR message.
          - The FMI (Filter Match Index) value.
          - An array containing the data.

        If *list* is ``None`` then a new tuple will be allocated, as well as a new
        bytes object to contain the data (as the fifth element in the tuple).

        If *list* is not ``None`` then it should be a list object with a least five
        elements.  The fifth element should be a memoryview object which is created
        from either a bytearray or an array of type 'B' or 'b', and this array must
        have enough room for at least 8 bytes.  The list object will then be
        populated with the first four return values above, and the memoryview object
        will be resized inplace to the size of the data and filled in with that data.
        The same list and memoryview objects can be reused in subsequent calls to
        this method, providing a way of receiving data without using the heap.
        For example::

             buf = bytearray(8)
             lst = [0, 0, 0, 0, memoryview(buf)]
             # No heap memory is allocated in the following call
             can.recv(0, lst)
        """

    def init(
        self,
        mode: int,
        /,
        extframe: bool = False,
        prescaler: int = 100,
        *,
        sjw: int = 1,
        bs1: int = 6,
        bs2: int = 8,
        auto_restart: bool = False,
        baudrate: int = 0,
        sample_point: int = 75,
    ) -> None:
        """
         Initialise the CAN bus with the given parameters:

           - *mode* is one of:  NORMAL, LOOPBACK, SILENT, SILENT_LOOPBACK
           - *prescaler* is the value by which the CAN input clock is divided to generate the
             nominal bit time quanta. The prescaler can be a value between 1 and 1024 inclusive
             for classic CAN, and between 1 and 512 inclusive for CAN FD.
           - *sjw* is the resynchronisation jump width in units of time quanta for nominal bits;
             it can be a value between 1 and 4 inclusive for classic CAN, and between 1 and 128 inclusive for CAN FD.
           - *bs1* defines the location of the sample point in units of the time quanta for nominal bits;
             it can be a value between 1 and 16 inclusive for classic CAN, and between 2 and 256 inclusive for CAN FD.
           - *bs2* defines the location of the transmit point in units of the time quanta for nominal bits;
             it can be a value between 1 and 8 inclusive for classic CAN, and between 2 and 128 inclusive for CAN FD.
           - *auto_restart* sets whether the controller will automatically try and restart
             communications after entering the bus-off state; if this is disabled then
             :meth:`~CAN.restart()` can be used to leave the bus-off state
           - *baudrate* if a baudrate other than 0 is provided, this function will try to automatically
             calculate the CAN nominal bit time (overriding *prescaler*, *bs1* and *bs2*) that satisfies
             both the *baudrate* (within .1%) and the desired *sample_point* (to the nearest 1%). For more precise
             control over the CAN timing, set the *prescaler*, *bs1* and *bs2* parameters directly.
           - *sample_point* specifies the position of the bit sample with respect to the whole nominal bit time,
             expressed as an integer percentage of the nominal bit time. The default *sample_point* is 75%.
             This parameter is ignored unless *baudrate* is set.
           - *num_filter_banks* for classic CAN, this is the number of banks that will be assigned to CAN(1),
             the rest of the 28 are assigned to CAN(2).

        The remaining parameters are only present on boards with CAN FD support, and configure the optional CAN FD
        Bit Rate Switch (BRS) feature:

           - *brs_prescaler* is the value by which the CAN FD input clock is divided to generate the
             data bit time quanta. The prescaler can be a value between 1 and 32 inclusive.
           - *brs_sjw* is the resynchronisation jump width in units of time quanta for data bits;
             it can be a value between 1 and 16 inclusive
           - *brs_bs1* defines the location of the sample point in units of the time quanta for data bits;
             it can be a value between 1 and 32 inclusive
           - *brs_bs2* defines the location of the transmit point in units of the time quanta for data bits;
             it can be a value between 1 and 16 inclusive
           - *brs_baudrate* if a baudrate other than 0 is provided, this function will try to automatically
             calculate the CAN data bit time (overriding *brs_prescaler*, *brs_bs1* and *brs_bs2*) that satisfies
             both the *brs_baudrate* (within .1%) and the desired *brs_sample_point* (to the nearest 1%). For more
             precise control over the BRS timing, set the *brs_prescaler*, *brs_bs1* and *brs_bs2* parameters directly.
           - *brs_sample_point* specifies the position of the bit sample with respect to the whole nominal bit time,
             expressed as an integer percentage of the nominal bit time. The default *brs_sample_point* is 75%.
             This parameter is ignored unless *brs_baudrate* is set.

         The time quanta tq is the basic unit of time for the CAN bus.  tq is the CAN
         prescaler value divided by PCLK1 (the frequency of internal peripheral bus 1);
         see :meth:`pyb.freq()` to determine PCLK1.

         A single bit is made up of the synchronisation segment, which is always 1 tq.
         Then follows bit segment 1, then bit segment 2.  The sample point is after bit
         segment 1 finishes.  The transmit point is after bit segment 2 finishes.
         The baud rate will be 1/bittime, where the bittime is 1 + BS1 + BS2 multiplied
         by the time quanta tq.

         For example, with PCLK1=42MHz, prescaler=100, sjw=1, bs1=6, bs2=8, the value of
         tq is 2.38 microseconds.  The bittime is 35.7 microseconds, and the baudrate
         is 28kHz.

         See page 680 of the STM32F405 datasheet for more details.
        """
        ...

    def rxcallback(self, fifo: int, fun: Callable[[CAN], None], /) -> None:
        """
        Register a function to be called when a message is accepted into a empty fifo:

        - *fifo* is the receiving fifo.
        - *fun* is the function to be called when the fifo becomes non empty.

        The callback function takes two arguments the first is the can object it self the second is
        a integer that indicates the reason for the callback.

        +--------+------------------------------------------------+
        | Reason |                                                |
        +========+================================================+
        | 0      | A message has been accepted into a empty FIFO. |
        +--------+------------------------------------------------+
        | 1      | The FIFO is full                               |
        +--------+------------------------------------------------+
        | 2      | A message has been lost due to a full FIFO     |
        +--------+------------------------------------------------+

        Example use of rxcallback::

          def cb0(bus, reason):
            print('cb0')
            if reason == 0:
                print('pending')
            if reason == 1:
                print('full')
            if reason == 2:
                print('overflow')

          can = CAN(1, CAN.LOOPBACK)
          can.rxcallback(0, cb0)
        """
        ...

    @overload
    def setfilter(self, bank: int, mode: int, fifo: int, params: Sequence[int], /) -> None:
        """
        Configure a filter bank:

        - *bank* is the classic CAN controller filter bank, or CAN FD filter index, to configure.
        - *mode* is the mode the filter should operate in, see the tables below.
        - *fifo* is which fifo (0 or 1) a message should be stored in, if it is accepted by this filter.
        - *params* is an array of values the defines the filter. The contents of the array depends on the *mode* argument.

        +-----------+---------------------------------------------------------+
        |*mode*     |Contents of *params* array for classic CAN controller    |
        +===========+=========================================================+
        |CAN.LIST16 |Four 16 bit ids that will be accepted                    |
        +-----------+---------------------------------------------------------+
        |CAN.LIST32 |Two 32 bit ids that will be accepted                     |
        +-----------+---------------------------------------------------------+
        |CAN.MASK16 |Two 16 bit id/mask pairs. E.g. (1, 3, 4, 4)              |
        |           | | The first pair, 1 and 3 will accept all ids           |
        |           | | that have bit 0 = 1 and bit 1 = 0.                    |
        |           | | The second pair, 4 and 4, will accept all ids         |
        |           | | that have bit 2 = 1.                                  |
        +-----------+---------------------------------------------------------+
        |CAN.MASK32 |As with CAN.MASK16 but with only one 32 bit id/mask pair.|
        +-----------+---------------------------------------------------------+

        +-----------+---------------------------------------------------------+
        |*mode*     |Contents of *params* array for CAN FD controller         |
        +===========+=========================================================+
        |CAN.RANGE  |Two ids that represent a range of accepted ids.          |
        +-----------+---------------------------------------------------------+
        |CAN.DUAL   |Two ids that will be accepted. For example (1, 2)        |
        +-----------+---------------------------------------------------------+
        |CAN.MASK   |One filter ID and a mask. For example (0x111, 0x7FF)     |
        +-----------+---------------------------------------------------------+

        - *rtr* For classic CAN controllers, this is an array of booleans that states if
          a filter should accept a remote transmission request message. If this argument
          is not given then it defaults to ``False`` for all entries. The length of the
          array depends on the *mode* argument. For CAN FD, this argument is ignored.

        +-----------+----------------------+
        |*mode*     |length of *rtr* array |
        +===========+======================+
        |CAN.LIST16 |4                     |
        +-----------+----------------------+
        |CAN.LIST32 |2                     |
        +-----------+----------------------+
        |CAN.MASK16 |2                     |
        +-----------+----------------------+
        |CAN.MASK32 |1                     |
        +-----------+----------------------+

        - *extframe* If True the frame will have an extended identifier (29 bits),
          otherwise a standard identifier (11 bits) is used.
        """

    @overload
    def setfilter(
        self,
        bank: int,
        mode: int,
        fifo: int,
        params: Sequence[int],
        /,
        *,
        rtr: Sequence[bool],
    ) -> None:
        """
        Configure a filter bank:

        - *bank* is the classic CAN controller filter bank, or CAN FD filter index, to configure.
        - *mode* is the mode the filter should operate in, see the tables below.
        - *fifo* is which fifo (0 or 1) a message should be stored in, if it is accepted by this filter.
        - *params* is an array of values the defines the filter. The contents of the array depends on the *mode* argument.

        +-----------+---------------------------------------------------------+
        |*mode*     |Contents of *params* array for classic CAN controller    |
        +===========+=========================================================+
        |CAN.LIST16 |Four 16 bit ids that will be accepted                    |
        +-----------+---------------------------------------------------------+
        |CAN.LIST32 |Two 32 bit ids that will be accepted                     |
        +-----------+---------------------------------------------------------+
        |CAN.MASK16 |Two 16 bit id/mask pairs. E.g. (1, 3, 4, 4)              |
        |           | | The first pair, 1 and 3 will accept all ids           |
        |           | | that have bit 0 = 1 and bit 1 = 0.                    |
        |           | | The second pair, 4 and 4, will accept all ids         |
        |           | | that have bit 2 = 1.                                  |
        +-----------+---------------------------------------------------------+
        |CAN.MASK32 |As with CAN.MASK16 but with only one 32 bit id/mask pair.|
        +-----------+---------------------------------------------------------+

        +-----------+---------------------------------------------------------+
        |*mode*     |Contents of *params* array for CAN FD controller         |
        +===========+=========================================================+
        |CAN.RANGE  |Two ids that represent a range of accepted ids.          |
        +-----------+---------------------------------------------------------+
        |CAN.DUAL   |Two ids that will be accepted. For example (1, 2)        |
        +-----------+---------------------------------------------------------+
        |CAN.MASK   |One filter ID and a mask. For example (0x111, 0x7FF)     |
        +-----------+---------------------------------------------------------+

        - *rtr* For classic CAN controllers, this is an array of booleans that states if
          a filter should accept a remote transmission request message. If this argument
          is not given then it defaults to ``False`` for all entries. The length of the
          array depends on the *mode* argument. For CAN FD, this argument is ignored.

        +-----------+----------------------+
        |*mode*     |length of *rtr* array |
        +===========+======================+
        |CAN.LIST16 |4                     |
        +-----------+----------------------+
        |CAN.LIST32 |2                     |
        +-----------+----------------------+
        |CAN.MASK16 |2                     |
        +-----------+----------------------+
        |CAN.MASK32 |1                     |
        +-----------+----------------------+

        - *extframe* If True the frame will have an extended identifier (29 bits),
          otherwise a standard identifier (11 bits) is used.
        """

    def state(self) -> int:
        """
        Return the state of the controller.  The return value can be one of:

        - ``CAN.STOPPED`` -- the controller is completely off and reset;
        - ``CAN.ERROR_ACTIVE`` -- the controller is on and in the Error Active state
          (both TEC and REC are less than 96);
        - ``CAN.ERROR_WARNING`` -- the controller is on and in the Error Warning state
          (at least one of TEC or REC is 96 or greater);
        - ``CAN.ERROR_PASSIVE`` -- the controller is on and in the Error Passive state
          (at least one of TEC or REC is 128 or greater);
        - ``CAN.BUS_OFF`` -- the controller is on but not participating in bus activity
          (TEC overflowed beyond 255).
        """
        ...

    def send(
        self,
        data: int | AnyWritableBuf,
        id: int,
        /,
        *,
        timeout: int = 0,
        rtr: bool = False,
    ) -> None:
        """
        Send a message on the bus:

          - *data* is the data to send (an integer to send, or a buffer object).
          - *id* is the id of the message to be sent.
          - *timeout* is the timeout in milliseconds to wait for the send.
          - *rtr* is a boolean that specifies if the message shall be sent as
            a remote transmission request.  If *rtr* is True then only the length
            of *data* is used to fill in the DLC slot of the frame; the actual
            bytes in *data* are unused.
          - *extframe* if True the frame will have an extended identifier (29 bits),
            otherwise a standard identifier (11 bits) is used.
          - *fdf* for CAN FD controllers, if set to True, the frame will have an FD
            frame format, which supports data payloads up to 64 bytes.
          - *brs* for CAN FD controllers, if set to True, the bitrate switching mode
            is enabled, in which the data phase is transmitted at a different bitrate.
            See :meth:`CAN.init` for the data bit timing configuration parameters.

          If timeout is 0 the message is placed in a buffer in one of three hardware
          buffers and the method returns immediately. If all three buffers are in use
          an exception is thrown. If timeout is not 0, the method waits until the
          message is transmitted. If the message can't be transmitted within the
          specified time an exception is thrown.

        Return value: ``None``.
        """
        ...

    def any(self, fifo: int, /) -> bool:
        """
        Return ``True`` if any message waiting on the FIFO, else ``False``.
        """
        ...

    @overload
    def info(self) -> list[int]:
        """
        Get information about the controller's error states and TX and RX buffers.
        If *list* is provided then it should be a list object with at least 8 entries,
        which will be filled in with the information.  Otherwise a new list will be
        created and filled in.  In both cases the return value of the method is the
        populated list.

        The values in the list are:

        - TEC value
        - REC value
        - number of times the controller enterted the Error Warning state (wrapped
          around to 0 after 65535)
        - number of times the controller enterted the Error Passive state (wrapped
          around to 0 after 65535)
        - number of times the controller enterted the Bus Off state (wrapped
          around to 0 after 65535)
        - number of pending TX messages
        - number of pending RX messages on fifo 0
        - number of pending RX messages on fifo 1
        """

    @overload
    def info(self, list: list[int], /) -> list[int]:
        """
        Get information about the controller's error states and TX and RX buffers.
        If *list* is provided then it should be a list object with at least 8 entries,
        which will be filled in with the information.  Otherwise a new list will be
        created and filled in.  In both cases the return value of the method is the
        populated list.

        The values in the list are:

        - TEC value
        - REC value
        - number of times the controller enterted the Error Warning state (wrapped
          around to 0 after 65535)
        - number of times the controller enterted the Error Passive state (wrapped
          around to 0 after 65535)
        - number of times the controller enterted the Bus Off state (wrapped
          around to 0 after 65535)
        - number of pending TX messages
        - number of pending RX messages on fifo 0
        - number of pending RX messages on fifo 1
        """

    def clearfilter(self, bank: int, /) -> None:
        """
        Clear and disables a filter bank:

        - *bank* is the classic CAN controller filter bank, or CAN FD filter index, to clear.
        - *extframe* For CAN FD controllers, if True, clear an extended filter (configured with extframe=True),
          otherwise the clear a standard identifier (configured with extframe=False).
        """
        ...

    def deinit(self) -> None:
        """
        Turn off the CAN bus.
        """
        ...

    def __init__(
        self,
        bus: int | str,
        mode: int,
        /,
        extframe: bool = False,
        prescaler: int = 100,
        *,
        sjw: int = 1,
        bs1: int = 6,
        bs2: int = 8,
        auto_restart: bool = False,
    ) -> None:
        """
        Construct a CAN object on the given bus.  *bus* can be 1-2, or ``'YA'`` or ``'YB'``.
        With no additional parameters, the CAN object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See :meth:`CAN.init` for parameters of initialisation.

        The physical pins of the CAN buses are:

          - ``CAN(1)`` is on ``YA``: ``(RX, TX) = (Y3, Y4) = (PB8, PB9)``
          - ``CAN(2)`` is on ``YB``: ``(RX, TX) = (Y5, Y6) = (PB12, PB13)``
        """

class ADC:
    """
    Usage::

        import pyb

        adc = pyb.ADC(pin)                  # create an analog object from a pin
        val = adc.read()                    # read an analog value

        adc = pyb.ADCAll(resolution)        # create an ADCAll object
        adc = pyb.ADCAll(resolution, mask)  # create an ADCAll object for selected analog channels
        val = adc.read_channel(channel)     # read the given channel
        val = adc.read_core_temp()          # read MCU temperature
        val = adc.read_core_vbat()          # read MCU VBAT
        val = adc.read_core_vref()          # read MCU VREF
        val = adc.read_vref()               # read MCU supply voltage
    """

    def read_timed(self, buf: AnyWritableBuf, timer: Timer | int, /) -> None:
        """
        Read analog values into ``buf`` at a rate set by the ``timer`` object.

        ``buf`` can be bytearray or array.array for example.  The ADC values have
        12-bit resolution and are stored directly into ``buf`` if its element size is
        16 bits or greater.  If ``buf`` has only 8-bit elements (eg a bytearray) then
        the sample resolution will be reduced to 8 bits.

        ``timer`` should be a Timer object, and a sample is read each time the timer
        triggers.  The timer must already be initialised and running at the desired
        sampling frequency.

        To support previous behaviour of this function, ``timer`` can also be an
        integer which specifies the frequency (in Hz) to sample at.  In this case
        Timer(6) will be automatically configured to run at the given frequency.

        Example using a Timer object (preferred way)::

            adc = pyb.ADC(pyb.Pin.board.X19)    # create an ADC on pin X19
            tim = pyb.Timer(6, freq=10)         # create a timer running at 10Hz
            buf = bytearray(100)                # creat a buffer to store the samples
            adc.read_timed(buf, tim)            # sample 100 values, taking 10s

        Example using an integer for the frequency::

            adc = pyb.ADC(pyb.Pin.board.X19)    # create an ADC on pin X19
            buf = bytearray(100)                # create a buffer of 100 bytes
            adc.read_timed(buf, 10)             # read analog values into buf at 10Hz
                                                #   this will take 10 seconds to finish
            for val in buf:                     # loop over all values
                print(val)                      # print the value out

        This function does not allocate any heap memory. It has blocking behaviour:
        it does not return to the calling program until the buffer is full.
        """
        ...

    @staticmethod
    def read_timed_multi(adcs: tuple[ADC, ...], bufs: tuple[AnyWritableBuf, ...], timer: Timer, /) -> bool:
        """
        This is a static method. It can be used to extract relative timing or
        phase data from multiple ADC's.

        It reads analog values from multiple ADC's into buffers at a rate set by
        the *timer* object. Each time the timer triggers a sample is rapidly
        read from each ADC in turn.

        ADC and buffer instances are passed in tuples with each ADC having an
        associated buffer. All buffers must be of the same type and length and
        the number of buffers must equal the number of ADC's.

        Buffers can be ``bytearray`` or ``array.array`` for example. The ADC values
        have 12-bit resolution and are stored directly into the buffer if its element
        size is 16 bits or greater.  If buffers have only 8-bit elements (eg a
        ``bytearray``) then the sample resolution will be reduced to 8 bits.

        *timer* must be a Timer object. The timer must already be initialised
        and running at the desired sampling frequency.

        Example reading 3 ADC's::

            adc0 = pyb.ADC(pyb.Pin.board.X1)    # Create ADC's
            adc1 = pyb.ADC(pyb.Pin.board.X2)
            adc2 = pyb.ADC(pyb.Pin.board.X3)
            tim = pyb.Timer(8, freq=100)        # Create timer
            rx0 = array.array('H', (0 for i in range(100))) # ADC buffers of
            rx1 = array.array('H', (0 for i in range(100))) # 100 16-bit words
            rx2 = array.array('H', (0 for i in range(100)))
            # read analog values into buffers at 100Hz (takes one second)
            pyb.ADC.read_timed_multi((adc0, adc1, adc2), (rx0, rx1, rx2), tim)
            for n in range(len(rx0)):
                print(rx0[n], rx1[n], rx2[n])

        This function does not allocate any heap memory. It has blocking behaviour:
        it does not return to the calling program until the buffers are full.

        The function returns ``True`` if all samples were acquired with correct
        timing. At high sample rates the time taken to acquire a set of samples
        can exceed the timer period. In this case the function returns ``False``,
        indicating a loss of precision in the sample interval. In extreme cases
        samples may be missed.

        The maximum rate depends on factors including the data width and the
        number of ADC's being read. In testing two ADC's were sampled at a timer
        rate of 210kHz without overrun. Samples were missed at 215kHz.  For three
        ADC's the limit is around 140kHz, and for four it is around 110kHz.
        At high sample rates disabling interrupts for the duration can reduce the
        risk of sporadic data loss.
        """
        ...

    def read(self) -> int:
        """
        Read the value on the analog pin and return it.  The returned value
        will be between 0 and 4095.
        """
        ...

    def __init__(self, pin: int | Pin, /) -> None:
        """
        Create an ADC object associated with the given pin.
        This allows you to then read analog values on that pin.
        """

class ADCAll:
    def read_core_vbat(self, *args, **kwargs) -> Incomplete: ...
    def read_core_vref(self, *args, **kwargs) -> Incomplete: ...
    def read_vref(self, *args, **kwargs) -> Incomplete: ...
    def read_core_temp(self, *args, **kwargs) -> Incomplete: ...
    def read_channel(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...

class Accel:
    """
    Accel is an object that controls the accelerometer.  Example usage::

        accel = pyb.Accel()
        for i in range(10):
            print(accel.x(), accel.y(), accel.z())

    Raw values are between -32 and 31.
    """

    def x(self) -> int:
        """
        Get the x-axis value.
        """
        ...

    def tilt(self) -> int:
        """
        Get the tilt register.
        """
        ...

    def y(self) -> int:
        """
        Get the y-axis value.
        """
        ...

    def z(self) -> int:
        """
        Get the z-axis value.
        """
        ...

    def read(self, *args, **kwargs) -> Incomplete: ...
    def filtered_xyz(self) -> Tuple:
        """
        Get a 3-tuple of filtered x, y and z values.

        Implementation note: this method is currently implemented as taking the
        sum of 4 samples, sampled from the 3 previous calls to this function along
        with the sample from the current call.  Returned values are therefore 4
        times the size of what they would be from the raw x(), y() and z() calls.
        """
        ...

    def write(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self) -> None:
        """
        Create and return an accelerometer object.
        """

class USB_VCP:
    """
    The USB_VCP class allows creation of a `stream`-like object representing the USB
    virtual comm port.  It can be used to read and write data over USB to
    the connected host.
    """

    RTS: Final[int] = 1
    CTS: Final[int] = 2
    IRQ_RX: Final[int] = 1
    def readlines(self) -> List:
        """
        Read as much data as possible from the serial device, breaking it into
        lines.

        Returns a list of bytes objects, each object being one of the lines.
        Each line will include the newline character.
        """
        ...

    @overload
    def recv(self, data: int, /, *, timeout: int = 5000) -> bytes | None:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    @overload
    def recv(self, data: AnyWritableBuf, /, *, timeout: int = 5000) -> int | None:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    def isconnected(self) -> bool:
        """
        Return ``True`` if USB is connected as a serial device, else ``False``.
        """
        ...

    def init(self, *, flow: int = -1) -> None:
        """
        Configure the USB VCP port.  If the *flow* argument is not -1 then the value sets
        the flow control, which can be a bitwise-or of ``USB_VCP.RTS`` and ``USB_VCP.CTS``.
        RTS is used to control read behaviour and CTS, to control write behaviour.
        """
        ...

    def irq(self, handler=None, trigger=IRQ_RX, hard=False) -> None:
        """
        Register *handler* to be called whenever an event specified by *trigger*
        occurs.  The *handler* function must take exactly one argument, which will
        be the USB VCP object.  Pass in ``None`` to disable the callback.

        Valid values for *trigger* are:

          - ``USB_VCP.IRQ_RX``: new data is available for reading from the USB VCP object.
        """
        ...

    def setinterrupt(self, chr: int, /) -> None:
        """
        Set the character which interrupts running Python code.  This is set
        to 3 (CTRL-C) by default, and when a CTRL-C character is received over
        the USB VCP port, a KeyboardInterrupt exception is raised.

        Set to -1 to disable this interrupt feature.  This is useful when you
        want to send raw bytes over the USB VCP port.
        """
        ...

    def close(self) -> None:
        """
        This method does nothing.  It exists so the USB_VCP object can act as
        a file.
        """
        ...

    @overload
    def read(self) -> bytes | None:
        """
        Read at most ``nbytes`` from the serial device and return them as a
        bytes object.  If ``nbytes`` is not specified then the method reads
        all available bytes from the serial device.
        USB_VCP `stream` implicitly works in non-blocking mode,
        so if no pending data available, this method will return immediately
        with ``None`` value.
        """

    @overload
    def read(self, nbytes, /) -> bytes | None:
        """
        Read at most ``nbytes`` from the serial device and return them as a
        bytes object.  If ``nbytes`` is not specified then the method reads
        all available bytes from the serial device.
        USB_VCP `stream` implicitly works in non-blocking mode,
        so if no pending data available, this method will return immediately
        with ``None`` value.
        """

    def any(self) -> bool:
        """
        Return ``True`` if any characters waiting, else ``False``.
        """
        ...

    def write(self, buf: AnyReadableBuf, /) -> int:
        """
        Write the bytes from ``buf`` to the serial device.

        Returns the number of bytes written.
        """
        ...

    def send(self, buf: AnyWritableBuf | bytes | int, /, *, timeout: int = 5000) -> int:
        """
        Send data over the USB VCP:

          - ``data`` is the data to send (an integer to send, or a buffer object).
          - ``timeout`` is the timeout in milliseconds to wait for the send.

        Return value: number of bytes sent.
        """
        ...

    @overload
    def readinto(self, buf: AnyWritableBuf, /) -> int | None:
        """
        Read bytes from the serial device and store them into ``buf``, which
        should be a buffer-like object.  At most ``len(buf)`` bytes are read.
        If ``maxlen`` is given and then at most ``min(maxlen, len(buf))`` bytes
        are read.

        Returns the number of bytes read and stored into ``buf`` or ``None``
        if no pending data available.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, maxlen: int, /) -> int | None:
        """
        Read bytes from the serial device and store them into ``buf``, which
        should be a buffer-like object.  At most ``len(buf)`` bytes are read.
        If ``maxlen`` is given and then at most ``min(maxlen, len(buf))`` bytes
        are read.

        Returns the number of bytes read and stored into ``buf`` or ``None``
        if no pending data available.
        """

    def readline(self) -> bytes:
        """
        Read a whole line from the serial device.

        Returns a bytes object containing the data, including the trailing
        newline character or ``None`` if no pending data available.
        """
        ...

    def __init__(self, id: int = 0, /) -> None:
        """
        Create a new USB_VCP object.  The *id* argument specifies which USB VCP port to
        use.
        """

class Timer:
    """
    Timers can be used for a great variety of tasks.  At the moment, only
    the simplest case is implemented: that of calling a function periodically.

    Each timer consists of a counter that counts up at a certain rate.  The rate
    at which it counts is the peripheral clock frequency (in Hz) divided by the
    timer prescaler.  When the counter reaches the timer period it triggers an
    event, and the counter resets back to zero.  By using the callback method,
    the timer event can call a Python function.

    Example usage to toggle an LED at a fixed frequency::

        tim = pyb.Timer(4)              # create a timer object using timer 4
        tim.init(freq=2)                # trigger at 2Hz
        tim.callback(lambda t:pyb.LED(1).toggle())

    Example using named function for the callback::

        def tick(timer):                # we will receive the timer object when being called
            print(timer.counter())      # show current timer's counter value
        tim = pyb.Timer(4, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
        tim.callback(tick)              # set the callback to our tick function

    Further examples::

        tim = pyb.Timer(4, freq=100)    # freq in Hz
        tim = pyb.Timer(4, prescaler=0, period=99)
        tim.counter()                   # get counter (can also set)
        tim.prescaler(2)                # set prescaler (can also get)
        tim.period(199)                 # set period (can also get)
        tim.callback(lambda t: ...)     # set callback for update interrupt (t=tim instance)
        tim.callback(None)              # clear callback

    *Note:* Timer(2) and Timer(3) are used for PWM to set the intensity of LED(3)
    and LED(4) respectively.  But these timers are only configured for PWM if
    the intensity of the relevant LED is set to a value between 1 and 254.  If
    the intensity feature of the LEDs is not used then these timers are free for
    general purpose use.  Similarly, Timer(5) controls the servo driver, and
    Timer(6) is used for timed ADC/DAC reading/writing.  It is recommended to
    use the other timers in your programs.

    *Note:* Memory can't be allocated during a callback (an interrupt) and so
    exceptions raised within a callback don't give much information.  See
    :func:`micropython.alloc_emergency_exception_buf` for how to get around this
    limitation.
    """

    OC_FORCED_ACTIVE: Final[int] = 6
    OC_FORCED_INACTIVE: Final[int] = 7
    OC_INACTIVE: Final[int] = 4
    OC_ACTIVE: Final[int] = 3
    LOW: Final[int] = 2
    IC: Final[int] = 8
    PWM_INVERTED: Final[int] = 1
    RISING: Final[int] = 0
    OC_TIMING: Final[int] = 2
    PWM: Final[int] = 0
    OC_TOGGLE: Final[int] = 5
    UP: Final[int] = 0
    BRK_LOW: Final[int] = 1
    BRK_OFF: Final[int] = 0
    CENTER: Final[int] = 32
    BRK_HIGH: Final[int] = 2
    BOTH: Final[int] = 10
    HIGH: Final[int] = 0
    ENC_B: Final[int] = 10
    FALLING: Final[int] = 2
    DOWN: Final[int] = 16
    ENC_AB: Final[int] = 11
    ENC_A: Final[int] = 9

    @overload
    def freq(self) -> int:
        """
        Get or set the frequency for the timer (changes prescaler and period if set).
        """

    @overload
    def freq(self, value: int, /) -> None:
        """
        Get or set the frequency for the timer (changes prescaler and period if set).
        """

    @overload
    def init(
        self,
        *,
        freq: int,
        mode: int = UP,
        div: int = 1,
        callback: Callable[[Timer], None] | None = None,
        deadtime: int = 0,
    ) -> None:
        """
        Initialise the timer.  Initialisation must be either by frequency (in Hz)
        or by prescaler and period::

            tim.init(freq=100)                  # set the timer to trigger at 100Hz
            tim.init(prescaler=83, period=999)  # set the prescaler and period directly

        Keyword arguments:

          - ``freq`` --- specifies the periodic frequency of the timer. You might also
            view this as the frequency with which the timer goes through one complete cycle.

          - ``prescaler`` [0-0xffff] - specifies the value to be loaded into the
            timer's Prescaler Register (PSC). The timer clock source is divided by
            (``prescaler + 1``) to arrive at the timer clock. Timers 2-7 and 12-14
            have a clock source of 84 MHz (pyb.freq()[2] * 2), and Timers 1, and 8-11
            have a clock source of 168 MHz (pyb.freq()[3] * 2).

          - ``period`` [0-0xffff] for timers 1, 3, 4, and 6-15. [0-0x3fffffff] for timers 2 & 5.
            Specifies the value to be loaded into the timer's AutoReload
            Register (ARR). This determines the period of the timer (i.e. when the
            counter cycles). The timer counter will roll-over after ``period + 1``
            timer clock cycles.

          - ``mode`` can be one of:

            - ``Timer.UP`` - configures the timer to count from 0 to ARR (default)
            - ``Timer.DOWN`` - configures the timer to count from ARR down to 0.
            - ``Timer.CENTER`` - configures the timer to count from 0 to ARR and
              then back down to 0.

          - ``div`` can be one of 1, 2, or 4. Divides the timer clock to determine
            the sampling clock used by the digital filters.

          - ``callback`` - as per Timer.callback()

          - ``deadtime`` - specifies the amount of "dead" or inactive time between
            transitions on complimentary channels (both channels will be inactive)
            for this time). ``deadtime`` may be an integer between 0 and 1008, with
            the following restrictions: 0-128 in steps of 1. 128-256 in steps of
            2, 256-512 in steps of 8, and 512-1008 in steps of 16. ``deadtime``
            measures ticks of ``source_freq`` divided by ``div`` clock ticks.
            ``deadtime`` is only available on timers 1 and 8.

          - ``brk`` - specifies if the break mode is used to kill the output of
            the PWM when the ``BRK_IN`` input is asserted. The value of this
            argument determines if break is enabled and what the polarity is, and
            can be one of ``Timer.BRK_OFF``, ``Timer.BRK_LOW`` or
            ``Timer.BRK_HIGH``. To select the ``BRK_IN`` pin construct a Pin object with
            ``mode=Pin.ALT, alt=Pin.AFn_TIMx``. The pin's GPIO input features are
            available in alt mode - ``pull=`` , ``value()`` and ``irq()``.

         You must either specify freq or both of period and prescaler.
        """

    @overload
    def init(
        self,
        *,
        prescaler: int,
        period: int,
        mode: int = UP,
        div: int = 1,
        callback: Callable[[Timer], None] | None = None,
        deadtime: int = 0,
    ) -> None:
        """
        Initialise the timer.  Initialisation must be either by frequency (in Hz)
        or by prescaler and period::

            tim.init(freq=100)                  # set the timer to trigger at 100Hz
            tim.init(prescaler=83, period=999)  # set the prescaler and period directly

        Keyword arguments:

          - ``freq`` --- specifies the periodic frequency of the timer. You might also
            view this as the frequency with which the timer goes through one complete cycle.

          - ``prescaler`` [0-0xffff] - specifies the value to be loaded into the
            timer's Prescaler Register (PSC). The timer clock source is divided by
            (``prescaler + 1``) to arrive at the timer clock. Timers 2-7 and 12-14
            have a clock source of 84 MHz (pyb.freq()[2] * 2), and Timers 1, and 8-11
            have a clock source of 168 MHz (pyb.freq()[3] * 2).

          - ``period`` [0-0xffff] for timers 1, 3, 4, and 6-15. [0-0x3fffffff] for timers 2 & 5.
            Specifies the value to be loaded into the timer's AutoReload
            Register (ARR). This determines the period of the timer (i.e. when the
            counter cycles). The timer counter will roll-over after ``period + 1``
            timer clock cycles.

          - ``mode`` can be one of:

            - ``Timer.UP`` - configures the timer to count from 0 to ARR (default)
            - ``Timer.DOWN`` - configures the timer to count from ARR down to 0.
            - ``Timer.CENTER`` - configures the timer to count from 0 to ARR and
              then back down to 0.

          - ``div`` can be one of 1, 2, or 4. Divides the timer clock to determine
            the sampling clock used by the digital filters.

          - ``callback`` - as per Timer.callback()

          - ``deadtime`` - specifies the amount of "dead" or inactive time between
            transitions on complimentary channels (both channels will be inactive)
            for this time). ``deadtime`` may be an integer between 0 and 1008, with
            the following restrictions: 0-128 in steps of 1. 128-256 in steps of
            2, 256-512 in steps of 8, and 512-1008 in steps of 16. ``deadtime``
            measures ticks of ``source_freq`` divided by ``div`` clock ticks.
            ``deadtime`` is only available on timers 1 and 8.

          - ``brk`` - specifies if the break mode is used to kill the output of
            the PWM when the ``BRK_IN`` input is asserted. The value of this
            argument determines if break is enabled and what the polarity is, and
            can be one of ``Timer.BRK_OFF``, ``Timer.BRK_LOW`` or
            ``Timer.BRK_HIGH``. To select the ``BRK_IN`` pin construct a Pin object with
            ``mode=Pin.ALT, alt=Pin.AFn_TIMx``. The pin's GPIO input features are
            available in alt mode - ``pull=`` , ``value()`` and ``irq()``.

         You must either specify freq or both of period and prescaler.
        """

    @overload
    def period(self) -> int:
        """
        Get or set the period of the timer.
        """

    @overload
    def period(self, value: int, /) -> None:
        """
        Get or set the period of the timer.
        """

    @overload
    def prescaler(self) -> int:
        """
        Get or set the prescaler for the timer.
        """

    @overload
    def prescaler(self, value: int, /) -> None:
        """
        Get or set the prescaler for the timer.
        """

    def source_freq(self) -> int:
        """
        Get the frequency of the source of the timer.
        """
        ...

    def deinit(self) -> None:
        """
        Deinitialises the timer.

        Disables the callback (and the associated irq).

        Disables any channel callbacks (and the associated irq).
        Stops the timer, and disables the timer peripheral.
        """
        ...

    def callback(self, fun: Callable[[Timer], None] | None, /) -> None:
        """
        Set the function to be called when the timer triggers.
        ``fun`` is passed 1 argument, the timer object.
        If ``fun`` is ``None`` then the callback will be disabled.
        """
        ...

    @overload
    def channel(self, channel: int, /) -> timerchannel | None:
        """
        If only a channel number is passed, then a previously initialized channel
        object is returned (or ``None`` if there is no previous channel).

        Otherwise, a TimerChannel object is initialized and returned.

        Each channel can be configured to perform pwm, output compare, or
        input capture. All channels share the same underlying timer, which means
        that they share the same timer clock.

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.PWM`` --- configure the timer in PWM mode (active high).
            - ``Timer.PWM_INVERTED`` --- configure the timer in PWM mode (active low).
            - ``Timer.OC_TIMING`` --- indicates that no pin is driven.
            - ``Timer.OC_ACTIVE`` --- the pin will be made active when a compare match occurs (active is determined by polarity)
            - ``Timer.OC_INACTIVE`` --- the pin will be made inactive when a compare match occurs.
            - ``Timer.OC_TOGGLE`` --- the pin will be toggled when an compare match occurs.
            - ``Timer.OC_FORCED_ACTIVE`` --- the pin is forced active (compare match is ignored).
            - ``Timer.OC_FORCED_INACTIVE`` --- the pin is forced inactive (compare match is ignored).
            - ``Timer.IC`` --- configure the timer in Input Capture mode.
            - ``Timer.ENC_A`` --- configure the timer in Encoder mode. The counter only changes when CH1 changes.
            - ``Timer.ENC_B`` --- configure the timer in Encoder mode. The counter only changes when CH2 changes.
            - ``Timer.ENC_AB`` --- configure the timer in Encoder mode. The counter changes when CH1 or CH2 changes.

          - ``callback`` - as per TimerChannel.callback()

          - ``pin`` None (the default) or a Pin object. If specified (and not None)
            this will cause the alternate function of the indicated pin
            to be configured for this timer channel. An error will be raised if
            the pin doesn't support any alternate functions for this timer channel.

        Keyword arguments for Timer.PWM modes:

          - ``pulse_width`` - determines the initial pulse width value to use.
          - ``pulse_width_percent`` - determines the initial pulse width percentage to use.

        Keyword arguments for Timer.OC modes:

          - ``compare`` - determines the initial value of the compare register.

          - ``polarity`` can be one of:

            - ``Timer.HIGH`` - output is active high
            - ``Timer.LOW`` - output is active low

        Optional keyword arguments for Timer.IC modes:

          - ``polarity`` can be one of:

            - ``Timer.RISING`` - captures on rising edge.
            - ``Timer.FALLING`` - captures on falling edge.
            - ``Timer.BOTH`` - captures on both edges.

          Note that capture only works on the primary channel, and not on the
          complimentary channels.

        Notes for Timer.ENC modes:

          - Requires 2 pins, so one or both pins will need to be configured to use
            the appropriate timer AF using the Pin API.
          - Read the encoder value using the timer.counter() method.
          - Only works on CH1 and CH2 (and not on CH1N or CH2N)
          - The channel number is ignored when setting the encoder mode.

        PWM Example::

            timer = pyb.Timer(2, freq=1000)
            ch2 = timer.channel(2, pyb.Timer.PWM, pin=pyb.Pin.board.X2, pulse_width=8000)
            ch3 = timer.channel(3, pyb.Timer.PWM, pin=pyb.Pin.board.X3, pulse_width=16000)

        PWM Motor Example with complementary outputs, dead time, break input and break callback::

            from pyb import Timer
            from machine import Pin # machine.Pin supports alt mode and irq on the same pin.
            pin_t8_1 = Pin(Pin.board.Y1, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PC6, TIM8_CH1
            pin_t8_1n = Pin(Pin.board.X8, mode=Pin.ALT, af=Pin.AF3_TIM8)  # Pin PA7, TIM8_CH1N
            pin_bkin = Pin(Pin.board.X7, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PA6, TIM8_BKIN
            pin_bkin.irq(handler=break_callabck, trigger=Pin.IRQ_FALLING)
            timer = pyb.Timer(8, freq=1000, deadtime=1008, brk=Timer.BRK_LOW)
            ch1 = timer.channel(1, pyb.Timer.PWM, pulse_width_percent=30)
        """

    @overload
    def channel(
        self,
        channel: int,
        /,
        mode: int,
        *,
        callback: Callable[[Timer], None] | None = None,
        pin: Pin | None = None,
        pulse_width: int,
    ) -> timerchannel:
        """
        If only a channel number is passed, then a previously initialized channel
        object is returned (or ``None`` if there is no previous channel).

        Otherwise, a TimerChannel object is initialized and returned.

        Each channel can be configured to perform pwm, output compare, or
        input capture. All channels share the same underlying timer, which means
        that they share the same timer clock.

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.PWM`` --- configure the timer in PWM mode (active high).
            - ``Timer.PWM_INVERTED`` --- configure the timer in PWM mode (active low).
            - ``Timer.OC_TIMING`` --- indicates that no pin is driven.
            - ``Timer.OC_ACTIVE`` --- the pin will be made active when a compare match occurs (active is determined by polarity)
            - ``Timer.OC_INACTIVE`` --- the pin will be made inactive when a compare match occurs.
            - ``Timer.OC_TOGGLE`` --- the pin will be toggled when an compare match occurs.
            - ``Timer.OC_FORCED_ACTIVE`` --- the pin is forced active (compare match is ignored).
            - ``Timer.OC_FORCED_INACTIVE`` --- the pin is forced inactive (compare match is ignored).
            - ``Timer.IC`` --- configure the timer in Input Capture mode.
            - ``Timer.ENC_A`` --- configure the timer in Encoder mode. The counter only changes when CH1 changes.
            - ``Timer.ENC_B`` --- configure the timer in Encoder mode. The counter only changes when CH2 changes.
            - ``Timer.ENC_AB`` --- configure the timer in Encoder mode. The counter changes when CH1 or CH2 changes.

          - ``callback`` - as per TimerChannel.callback()

          - ``pin`` None (the default) or a Pin object. If specified (and not None)
            this will cause the alternate function of the indicated pin
            to be configured for this timer channel. An error will be raised if
            the pin doesn't support any alternate functions for this timer channel.

        Keyword arguments for Timer.PWM modes:

          - ``pulse_width`` - determines the initial pulse width value to use.
          - ``pulse_width_percent`` - determines the initial pulse width percentage to use.

        Keyword arguments for Timer.OC modes:

          - ``compare`` - determines the initial value of the compare register.

          - ``polarity`` can be one of:

            - ``Timer.HIGH`` - output is active high
            - ``Timer.LOW`` - output is active low

        Optional keyword arguments for Timer.IC modes:

          - ``polarity`` can be one of:

            - ``Timer.RISING`` - captures on rising edge.
            - ``Timer.FALLING`` - captures on falling edge.
            - ``Timer.BOTH`` - captures on both edges.

          Note that capture only works on the primary channel, and not on the
          complimentary channels.

        Notes for Timer.ENC modes:

          - Requires 2 pins, so one or both pins will need to be configured to use
            the appropriate timer AF using the Pin API.
          - Read the encoder value using the timer.counter() method.
          - Only works on CH1 and CH2 (and not on CH1N or CH2N)
          - The channel number is ignored when setting the encoder mode.

        PWM Example::

            timer = pyb.Timer(2, freq=1000)
            ch2 = timer.channel(2, pyb.Timer.PWM, pin=pyb.Pin.board.X2, pulse_width=8000)
            ch3 = timer.channel(3, pyb.Timer.PWM, pin=pyb.Pin.board.X3, pulse_width=16000)

        PWM Motor Example with complementary outputs, dead time, break input and break callback::

            from pyb import Timer
            from machine import Pin # machine.Pin supports alt mode and irq on the same pin.
            pin_t8_1 = Pin(Pin.board.Y1, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PC6, TIM8_CH1
            pin_t8_1n = Pin(Pin.board.X8, mode=Pin.ALT, af=Pin.AF3_TIM8)  # Pin PA7, TIM8_CH1N
            pin_bkin = Pin(Pin.board.X7, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PA6, TIM8_BKIN
            pin_bkin.irq(handler=break_callabck, trigger=Pin.IRQ_FALLING)
            timer = pyb.Timer(8, freq=1000, deadtime=1008, brk=Timer.BRK_LOW)
            ch1 = timer.channel(1, pyb.Timer.PWM, pulse_width_percent=30)
        """

    @overload
    def channel(
        self,
        channel: int,
        /,
        mode: int,
        *,
        callback: Callable[[Timer], None] | None = None,
        pin: Pin | None = None,
        pulse_width_percent: int | float,
    ) -> timerchannel:
        """
        If only a channel number is passed, then a previously initialized channel
        object is returned (or ``None`` if there is no previous channel).

        Otherwise, a TimerChannel object is initialized and returned.

        Each channel can be configured to perform pwm, output compare, or
        input capture. All channels share the same underlying timer, which means
        that they share the same timer clock.

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.PWM`` --- configure the timer in PWM mode (active high).
            - ``Timer.PWM_INVERTED`` --- configure the timer in PWM mode (active low).
            - ``Timer.OC_TIMING`` --- indicates that no pin is driven.
            - ``Timer.OC_ACTIVE`` --- the pin will be made active when a compare match occurs (active is determined by polarity)
            - ``Timer.OC_INACTIVE`` --- the pin will be made inactive when a compare match occurs.
            - ``Timer.OC_TOGGLE`` --- the pin will be toggled when an compare match occurs.
            - ``Timer.OC_FORCED_ACTIVE`` --- the pin is forced active (compare match is ignored).
            - ``Timer.OC_FORCED_INACTIVE`` --- the pin is forced inactive (compare match is ignored).
            - ``Timer.IC`` --- configure the timer in Input Capture mode.
            - ``Timer.ENC_A`` --- configure the timer in Encoder mode. The counter only changes when CH1 changes.
            - ``Timer.ENC_B`` --- configure the timer in Encoder mode. The counter only changes when CH2 changes.
            - ``Timer.ENC_AB`` --- configure the timer in Encoder mode. The counter changes when CH1 or CH2 changes.

          - ``callback`` - as per TimerChannel.callback()

          - ``pin`` None (the default) or a Pin object. If specified (and not None)
            this will cause the alternate function of the indicated pin
            to be configured for this timer channel. An error will be raised if
            the pin doesn't support any alternate functions for this timer channel.

        Keyword arguments for Timer.PWM modes:

          - ``pulse_width`` - determines the initial pulse width value to use.
          - ``pulse_width_percent`` - determines the initial pulse width percentage to use.

        Keyword arguments for Timer.OC modes:

          - ``compare`` - determines the initial value of the compare register.

          - ``polarity`` can be one of:

            - ``Timer.HIGH`` - output is active high
            - ``Timer.LOW`` - output is active low

        Optional keyword arguments for Timer.IC modes:

          - ``polarity`` can be one of:

            - ``Timer.RISING`` - captures on rising edge.
            - ``Timer.FALLING`` - captures on falling edge.
            - ``Timer.BOTH`` - captures on both edges.

          Note that capture only works on the primary channel, and not on the
          complimentary channels.

        Notes for Timer.ENC modes:

          - Requires 2 pins, so one or both pins will need to be configured to use
            the appropriate timer AF using the Pin API.
          - Read the encoder value using the timer.counter() method.
          - Only works on CH1 and CH2 (and not on CH1N or CH2N)
          - The channel number is ignored when setting the encoder mode.

        PWM Example::

            timer = pyb.Timer(2, freq=1000)
            ch2 = timer.channel(2, pyb.Timer.PWM, pin=pyb.Pin.board.X2, pulse_width=8000)
            ch3 = timer.channel(3, pyb.Timer.PWM, pin=pyb.Pin.board.X3, pulse_width=16000)

        PWM Motor Example with complementary outputs, dead time, break input and break callback::

            from pyb import Timer
            from machine import Pin # machine.Pin supports alt mode and irq on the same pin.
            pin_t8_1 = Pin(Pin.board.Y1, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PC6, TIM8_CH1
            pin_t8_1n = Pin(Pin.board.X8, mode=Pin.ALT, af=Pin.AF3_TIM8)  # Pin PA7, TIM8_CH1N
            pin_bkin = Pin(Pin.board.X7, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PA6, TIM8_BKIN
            pin_bkin.irq(handler=break_callabck, trigger=Pin.IRQ_FALLING)
            timer = pyb.Timer(8, freq=1000, deadtime=1008, brk=Timer.BRK_LOW)
            ch1 = timer.channel(1, pyb.Timer.PWM, pulse_width_percent=30)
        """

    @overload
    def channel(
        self,
        channel: int,
        /,
        mode: int,
        *,
        callback: Callable[[Timer], None] | None = None,
        pin: Pin | None = None,
        compare: int,
        polarity: int,
    ) -> timerchannel:
        """
        If only a channel number is passed, then a previously initialized channel
        object is returned (or ``None`` if there is no previous channel).

        Otherwise, a TimerChannel object is initialized and returned.

        Each channel can be configured to perform pwm, output compare, or
        input capture. All channels share the same underlying timer, which means
        that they share the same timer clock.

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.PWM`` --- configure the timer in PWM mode (active high).
            - ``Timer.PWM_INVERTED`` --- configure the timer in PWM mode (active low).
            - ``Timer.OC_TIMING`` --- indicates that no pin is driven.
            - ``Timer.OC_ACTIVE`` --- the pin will be made active when a compare match occurs (active is determined by polarity)
            - ``Timer.OC_INACTIVE`` --- the pin will be made inactive when a compare match occurs.
            - ``Timer.OC_TOGGLE`` --- the pin will be toggled when an compare match occurs.
            - ``Timer.OC_FORCED_ACTIVE`` --- the pin is forced active (compare match is ignored).
            - ``Timer.OC_FORCED_INACTIVE`` --- the pin is forced inactive (compare match is ignored).
            - ``Timer.IC`` --- configure the timer in Input Capture mode.
            - ``Timer.ENC_A`` --- configure the timer in Encoder mode. The counter only changes when CH1 changes.
            - ``Timer.ENC_B`` --- configure the timer in Encoder mode. The counter only changes when CH2 changes.
            - ``Timer.ENC_AB`` --- configure the timer in Encoder mode. The counter changes when CH1 or CH2 changes.

          - ``callback`` - as per TimerChannel.callback()

          - ``pin`` None (the default) or a Pin object. If specified (and not None)
            this will cause the alternate function of the indicated pin
            to be configured for this timer channel. An error will be raised if
            the pin doesn't support any alternate functions for this timer channel.

        Keyword arguments for Timer.PWM modes:

          - ``pulse_width`` - determines the initial pulse width value to use.
          - ``pulse_width_percent`` - determines the initial pulse width percentage to use.

        Keyword arguments for Timer.OC modes:

          - ``compare`` - determines the initial value of the compare register.

          - ``polarity`` can be one of:

            - ``Timer.HIGH`` - output is active high
            - ``Timer.LOW`` - output is active low

        Optional keyword arguments for Timer.IC modes:

          - ``polarity`` can be one of:

            - ``Timer.RISING`` - captures on rising edge.
            - ``Timer.FALLING`` - captures on falling edge.
            - ``Timer.BOTH`` - captures on both edges.

          Note that capture only works on the primary channel, and not on the
          complimentary channels.

        Notes for Timer.ENC modes:

          - Requires 2 pins, so one or both pins will need to be configured to use
            the appropriate timer AF using the Pin API.
          - Read the encoder value using the timer.counter() method.
          - Only works on CH1 and CH2 (and not on CH1N or CH2N)
          - The channel number is ignored when setting the encoder mode.

        PWM Example::

            timer = pyb.Timer(2, freq=1000)
            ch2 = timer.channel(2, pyb.Timer.PWM, pin=pyb.Pin.board.X2, pulse_width=8000)
            ch3 = timer.channel(3, pyb.Timer.PWM, pin=pyb.Pin.board.X3, pulse_width=16000)

        PWM Motor Example with complementary outputs, dead time, break input and break callback::

            from pyb import Timer
            from machine import Pin # machine.Pin supports alt mode and irq on the same pin.
            pin_t8_1 = Pin(Pin.board.Y1, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PC6, TIM8_CH1
            pin_t8_1n = Pin(Pin.board.X8, mode=Pin.ALT, af=Pin.AF3_TIM8)  # Pin PA7, TIM8_CH1N
            pin_bkin = Pin(Pin.board.X7, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PA6, TIM8_BKIN
            pin_bkin.irq(handler=break_callabck, trigger=Pin.IRQ_FALLING)
            timer = pyb.Timer(8, freq=1000, deadtime=1008, brk=Timer.BRK_LOW)
            ch1 = timer.channel(1, pyb.Timer.PWM, pulse_width_percent=30)
        """

    @overload
    def channel(
        self,
        channel: int,
        /,
        mode: int,
        *,
        callback: Callable[[Timer], None] | None = None,
        pin: Pin | None = None,
        polarity: int,
    ) -> timerchannel:
        """
        If only a channel number is passed, then a previously initialized channel
        object is returned (or ``None`` if there is no previous channel).

        Otherwise, a TimerChannel object is initialized and returned.

        Each channel can be configured to perform pwm, output compare, or
        input capture. All channels share the same underlying timer, which means
        that they share the same timer clock.

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.PWM`` --- configure the timer in PWM mode (active high).
            - ``Timer.PWM_INVERTED`` --- configure the timer in PWM mode (active low).
            - ``Timer.OC_TIMING`` --- indicates that no pin is driven.
            - ``Timer.OC_ACTIVE`` --- the pin will be made active when a compare match occurs (active is determined by polarity)
            - ``Timer.OC_INACTIVE`` --- the pin will be made inactive when a compare match occurs.
            - ``Timer.OC_TOGGLE`` --- the pin will be toggled when an compare match occurs.
            - ``Timer.OC_FORCED_ACTIVE`` --- the pin is forced active (compare match is ignored).
            - ``Timer.OC_FORCED_INACTIVE`` --- the pin is forced inactive (compare match is ignored).
            - ``Timer.IC`` --- configure the timer in Input Capture mode.
            - ``Timer.ENC_A`` --- configure the timer in Encoder mode. The counter only changes when CH1 changes.
            - ``Timer.ENC_B`` --- configure the timer in Encoder mode. The counter only changes when CH2 changes.
            - ``Timer.ENC_AB`` --- configure the timer in Encoder mode. The counter changes when CH1 or CH2 changes.

          - ``callback`` - as per TimerChannel.callback()

          - ``pin`` None (the default) or a Pin object. If specified (and not None)
            this will cause the alternate function of the indicated pin
            to be configured for this timer channel. An error will be raised if
            the pin doesn't support any alternate functions for this timer channel.

        Keyword arguments for Timer.PWM modes:

          - ``pulse_width`` - determines the initial pulse width value to use.
          - ``pulse_width_percent`` - determines the initial pulse width percentage to use.

        Keyword arguments for Timer.OC modes:

          - ``compare`` - determines the initial value of the compare register.

          - ``polarity`` can be one of:

            - ``Timer.HIGH`` - output is active high
            - ``Timer.LOW`` - output is active low

        Optional keyword arguments for Timer.IC modes:

          - ``polarity`` can be one of:

            - ``Timer.RISING`` - captures on rising edge.
            - ``Timer.FALLING`` - captures on falling edge.
            - ``Timer.BOTH`` - captures on both edges.

          Note that capture only works on the primary channel, and not on the
          complimentary channels.

        Notes for Timer.ENC modes:

          - Requires 2 pins, so one or both pins will need to be configured to use
            the appropriate timer AF using the Pin API.
          - Read the encoder value using the timer.counter() method.
          - Only works on CH1 and CH2 (and not on CH1N or CH2N)
          - The channel number is ignored when setting the encoder mode.

        PWM Example::

            timer = pyb.Timer(2, freq=1000)
            ch2 = timer.channel(2, pyb.Timer.PWM, pin=pyb.Pin.board.X2, pulse_width=8000)
            ch3 = timer.channel(3, pyb.Timer.PWM, pin=pyb.Pin.board.X3, pulse_width=16000)

        PWM Motor Example with complementary outputs, dead time, break input and break callback::

            from pyb import Timer
            from machine import Pin # machine.Pin supports alt mode and irq on the same pin.
            pin_t8_1 = Pin(Pin.board.Y1, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PC6, TIM8_CH1
            pin_t8_1n = Pin(Pin.board.X8, mode=Pin.ALT, af=Pin.AF3_TIM8)  # Pin PA7, TIM8_CH1N
            pin_bkin = Pin(Pin.board.X7, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PA6, TIM8_BKIN
            pin_bkin.irq(handler=break_callabck, trigger=Pin.IRQ_FALLING)
            timer = pyb.Timer(8, freq=1000, deadtime=1008, brk=Timer.BRK_LOW)
            ch1 = timer.channel(1, pyb.Timer.PWM, pulse_width_percent=30)
        """

    @overload
    def channel(
        self,
        channel: int,
        /,
        mode: int,
        *,
        callback: Callable[[Timer], None] | None = None,
        pin: Pin | None = None,
    ) -> timerchannel:
        """
        If only a channel number is passed, then a previously initialized channel
        object is returned (or ``None`` if there is no previous channel).

        Otherwise, a TimerChannel object is initialized and returned.

        Each channel can be configured to perform pwm, output compare, or
        input capture. All channels share the same underlying timer, which means
        that they share the same timer clock.

        Keyword arguments:

          - ``mode`` can be one of:

            - ``Timer.PWM`` --- configure the timer in PWM mode (active high).
            - ``Timer.PWM_INVERTED`` --- configure the timer in PWM mode (active low).
            - ``Timer.OC_TIMING`` --- indicates that no pin is driven.
            - ``Timer.OC_ACTIVE`` --- the pin will be made active when a compare match occurs (active is determined by polarity)
            - ``Timer.OC_INACTIVE`` --- the pin will be made inactive when a compare match occurs.
            - ``Timer.OC_TOGGLE`` --- the pin will be toggled when an compare match occurs.
            - ``Timer.OC_FORCED_ACTIVE`` --- the pin is forced active (compare match is ignored).
            - ``Timer.OC_FORCED_INACTIVE`` --- the pin is forced inactive (compare match is ignored).
            - ``Timer.IC`` --- configure the timer in Input Capture mode.
            - ``Timer.ENC_A`` --- configure the timer in Encoder mode. The counter only changes when CH1 changes.
            - ``Timer.ENC_B`` --- configure the timer in Encoder mode. The counter only changes when CH2 changes.
            - ``Timer.ENC_AB`` --- configure the timer in Encoder mode. The counter changes when CH1 or CH2 changes.

          - ``callback`` - as per TimerChannel.callback()

          - ``pin`` None (the default) or a Pin object. If specified (and not None)
            this will cause the alternate function of the indicated pin
            to be configured for this timer channel. An error will be raised if
            the pin doesn't support any alternate functions for this timer channel.

        Keyword arguments for Timer.PWM modes:

          - ``pulse_width`` - determines the initial pulse width value to use.
          - ``pulse_width_percent`` - determines the initial pulse width percentage to use.

        Keyword arguments for Timer.OC modes:

          - ``compare`` - determines the initial value of the compare register.

          - ``polarity`` can be one of:

            - ``Timer.HIGH`` - output is active high
            - ``Timer.LOW`` - output is active low

        Optional keyword arguments for Timer.IC modes:

          - ``polarity`` can be one of:

            - ``Timer.RISING`` - captures on rising edge.
            - ``Timer.FALLING`` - captures on falling edge.
            - ``Timer.BOTH`` - captures on both edges.

          Note that capture only works on the primary channel, and not on the
          complimentary channels.

        Notes for Timer.ENC modes:

          - Requires 2 pins, so one or both pins will need to be configured to use
            the appropriate timer AF using the Pin API.
          - Read the encoder value using the timer.counter() method.
          - Only works on CH1 and CH2 (and not on CH1N or CH2N)
          - The channel number is ignored when setting the encoder mode.

        PWM Example::

            timer = pyb.Timer(2, freq=1000)
            ch2 = timer.channel(2, pyb.Timer.PWM, pin=pyb.Pin.board.X2, pulse_width=8000)
            ch3 = timer.channel(3, pyb.Timer.PWM, pin=pyb.Pin.board.X3, pulse_width=16000)

        PWM Motor Example with complementary outputs, dead time, break input and break callback::

            from pyb import Timer
            from machine import Pin # machine.Pin supports alt mode and irq on the same pin.
            pin_t8_1 = Pin(Pin.board.Y1, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PC6, TIM8_CH1
            pin_t8_1n = Pin(Pin.board.X8, mode=Pin.ALT, af=Pin.AF3_TIM8)  # Pin PA7, TIM8_CH1N
            pin_bkin = Pin(Pin.board.X7, mode=Pin.ALT, af=Pin.AF3_TIM8)   # Pin PA6, TIM8_BKIN
            pin_bkin.irq(handler=break_callabck, trigger=Pin.IRQ_FALLING)
            timer = pyb.Timer(8, freq=1000, deadtime=1008, brk=Timer.BRK_LOW)
            ch1 = timer.channel(1, pyb.Timer.PWM, pulse_width_percent=30)
        """

    @overload
    def counter(self) -> int:
        """
        Get or set the timer counter.
        """

    @overload
    def counter(self, value: int, /) -> None:
        """
        Get or set the timer counter.
        """

    @overload
    def __init__(self, id: int, /):
        """
        Construct a new timer object of the given id.  If additional
        arguments are given, then the timer is initialised by ``init(...)``.
        ``id`` can be 1 to 14.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        *,
        freq: int,
        mode: int = UP,
        div: int = 1,
        callback: Callable[[Timer], None] | None = None,
        deadtime: int = 0,
    ):
        """
        Construct a new timer object of the given id.  If additional
        arguments are given, then the timer is initialised by ``init(...)``.
        ``id`` can be 1 to 14.
        """

    @overload
    def __init__(
        self,
        id: int,
        /,
        *,
        prescaler: int,
        period: int,
        mode: int = UP,
        div: int = 1,
        callback: Callable[[Timer], None] | None = None,
        deadtime: int = 0,
    ):
        """
        Construct a new timer object of the given id.  If additional
        arguments are given, then the timer is initialised by ``init(...)``.
        ``id`` can be 1 to 14.
        """

class Switch:
    """
    A Switch object is used to control a push-button switch.

    Usage::

         sw = pyb.Switch()       # create a switch object
         sw.value()              # get state (True if pressed, False otherwise)
         sw()                    # shorthand notation to get the switch state
         sw.callback(f)          # register a callback to be called when the
                                 #   switch is pressed down
         sw.callback(None)       # remove the callback

    Example::

         pyb.Switch().callback(lambda: pyb.LED(1).toggle())
    """

    def callback(self, fun: Callable[[], None] | None) -> None:
        """
        Register the given function to be called when the switch is pressed down.
        If ``fun`` is ``None``, then it disables the callback.
        """
        ...

    def value(self) -> bool:
        """
        Get the switch state.  Returns ``True`` if pressed down, otherwise ``False``.
        """
        ...

    def __init__(self) -> None:
        """
        Create and return a switch object.
        """

    @overload
    def __call__(self) -> bool:
        """
        Call switch object directly to get its state: ``True`` if pressed down,
        ``False`` otherwise.
        """
        ...

    @overload
    def __call__(self) -> bool:
        """
        Call switch object directly to get its state: ``True`` if pressed down,
        ``False`` otherwise.
        """
        ...

class Servo:
    """
    Servo objects control standard hobby servo motors with 3-wires (ground, power,
    signal).  There are 4 positions on the pyboard where these motors can be plugged
    in: pins X1 through X4 are the signal pins, and next to them are 4 sets of power
    and ground pins.

    Example usage::

        import pyb

        s1 = pyb.Servo(1)   # create a servo object on position X1
        s2 = pyb.Servo(2)   # create a servo object on position X2

        s1.angle(45)        # move servo 1 to 45 degrees
        s2.angle(0)         # move servo 2 to 0 degrees

        # move servo1 and servo2 synchronously, taking 1500ms
        s1.angle(-60, 1500)
        s2.angle(30, 1500)

    .. note:: The Servo objects use Timer(5) to produce the PWM output.  You can
       use Timer(5) for Servo control, or your own purposes, but not both at the
       same time.
    """

    @overload
    def speed(self) -> int:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    @overload
    def speed(self, speed: int, time: int = 0, /) -> None:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    @overload
    def speed(self) -> int:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    @overload
    def speed(self, value: int, /) -> None:
        """
        If no arguments are given, this function returns the current speed.

        If arguments are given, this function sets the speed of the servo:

          - ``speed`` is the speed to change to, between -100 and 100.
          - ``time`` is the number of milliseconds to take to get to the specified
            speed.  If omitted, then the servo accelerates as quickly as possible.
        """

    def pulse_width(self, value: Any | None = None) -> Incomplete:
        """
        If no arguments are given, this function returns the current raw pulse-width
        value.

        If an argument is given, this function sets the raw pulse-width value.
        """
        ...

    @overload
    def calibration(self) -> tuple[int, int, int, int, int]:
        """
        If no arguments are given, this function returns the current calibration
        data, as a 5-tuple.

        If arguments are given, this function sets the timing calibration:

          - ``pulse_min`` is the minimum allowed pulse width.
          - ``pulse_max`` is the maximum allowed pulse width.
          - ``pulse_centre`` is the pulse width corresponding to the centre/zero position.
          - ``pulse_angle_90`` is the pulse width corresponding to 90 degrees.
          - ``pulse_speed_100`` is the pulse width corresponding to a speed of 100.
        """

    @overload
    def calibration(self, pulse_min: int, pulse_max: int, pulse_centre: int, /) -> None:
        """
        If no arguments are given, this function returns the current calibration
        data, as a 5-tuple.

        If arguments are given, this function sets the timing calibration:

          - ``pulse_min`` is the minimum allowed pulse width.
          - ``pulse_max`` is the maximum allowed pulse width.
          - ``pulse_centre`` is the pulse width corresponding to the centre/zero position.
          - ``pulse_angle_90`` is the pulse width corresponding to 90 degrees.
          - ``pulse_speed_100`` is the pulse width corresponding to a speed of 100.
        """

    @overload
    def calibration(
        self,
        pulse_min: int,
        pulse_max: int,
        pulse_centre: int,
        pulse_angle_90: int,
        pulse_speed_100: int,
        /,
    ) -> None:
        """
        If no arguments are given, this function returns the current calibration
        data, as a 5-tuple.

        If arguments are given, this function sets the timing calibration:

          - ``pulse_min`` is the minimum allowed pulse width.
          - ``pulse_max`` is the maximum allowed pulse width.
          - ``pulse_centre`` is the pulse width corresponding to the centre/zero position.
          - ``pulse_angle_90`` is the pulse width corresponding to 90 degrees.
          - ``pulse_speed_100`` is the pulse width corresponding to a speed of 100.
        """

    @overload
    def angle(self) -> int:
        """
        If no arguments are given, this function returns the current angle.

        If arguments are given, this function sets the angle of the servo:

          - ``angle`` is the angle to move to in degrees.
          - ``time`` is the number of milliseconds to take to get to the specified
            angle.  If omitted, then the servo moves as quickly as possible to its
            new position.
        """

    @overload
    def angle(self, angle: int, time: int = 0, /) -> None:
        """
        If no arguments are given, this function returns the current angle.

        If arguments are given, this function sets the angle of the servo:

          - ``angle`` is the angle to move to in degrees.
          - ``time`` is the number of milliseconds to take to get to the specified
            angle.  If omitted, then the servo moves as quickly as possible to its
            new position.
        """

    def __init__(self, id: int, /) -> None:
        """
        Create a servo object.  ``id`` is 1-4, and corresponds to pins X1 through X4.
        """

class UART:
    """
    UART implements the standard UART/USART duplex serial communications protocol.  At
    the physical level it consists of 2 lines: RX and TX.  The unit of communication
    is a character (not to be confused with a string character) which can be 8 or 9
    bits wide.

    UART objects can be created and initialised using::

        from pyb import UART

        uart = UART(1, 9600)                         # init with given baudrate
        uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

    Bits can be 7, 8 or 9.  Parity can be None, 0 (even) or 1 (odd).  Stop can be 1 or 2.

    *Note:* with parity=None, only 8 and 9 bits are supported.  With parity enabled,
    only 7 and 8 bits are supported.

    A UART object acts like a `stream` object and reading and writing is done
    using the standard stream methods::

        uart.read(10)       # read 10 characters, returns a bytes object
        uart.read()         # read all available characters
        uart.readline()     # read a line
        uart.readinto(buf)  # read and store into the given buffer
        uart.write('abc')   # write the 3 characters

    Individual characters can be read/written using::

        uart.readchar()     # read 1 character and returns it as an integer
        uart.writechar(42)  # write 1 character

    To check if there is anything to be read, use::

        uart.any()          # returns the number of characters waiting


    *Note:* The stream functions ``read``, ``write``, etc. are new in MicroPython v1.3.4.
    Earlier versions use ``uart.send`` and ``uart.recv``.
    """

    CTS: Final[int] = 512
    IRQ_RX: Final[int] = 32
    IRQ_RXIDLE: Final[int] = 16
    RTS: Final[int] = 256
    def flush(self, *args, **kwargs) -> Incomplete: ...
    def sendbreak(self) -> None:
        """
        Send a break condition on the bus.  This drives the bus low for a duration
        of 13 bits.
        Return value: ``None``.
        """
        ...

    def txdone(self, *args, **kwargs) -> Incomplete: ...
    def init(
        self,
        baudrate: int,
        /,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        timeout: int = 0,
        flow: int = 0,
        timeout_char: int = 0,
        read_buf_len: int = 64,
    ):
        """
        Initialise the UART bus with the given parameters:

          - ``baudrate`` is the clock rate.
          - ``bits`` is the number of bits per character, 7, 8 or 9.
          - ``parity`` is the parity, ``None``, 0 (even) or 1 (odd).
          - ``stop`` is the number of stop bits, 1 or 2.
          - ``flow`` sets the flow control type. Can be 0, ``UART.RTS``, ``UART.CTS``
            or ``UART.RTS | UART.CTS``.
          - ``timeout`` is the timeout in milliseconds to wait for writing/reading the first character.
          - ``timeout_char`` is the timeout in milliseconds to wait between characters while writing or reading.
          - ``read_buf_len`` is the character length of the read buffer (0 to disable).

        This method will raise an exception if the baudrate could not be set within
        5% of the desired value.  The minimum baudrate is dictated by the frequency
        of the bus that the UART is on; UART(1) and UART(6) are APB2, the rest are on
        APB1.  The default bus frequencies give a minimum baudrate of 1300 for
        UART(1) and UART(6) and 650 for the others.  Use :func:`pyb.freq <pyb.freq>`
        to reduce the bus frequencies to get lower baudrates.

        *Note:* with parity=None, only 8 and 9 bits are supported.  With parity enabled,
        only 7 and 8 bits are supported.
        """
        ...

    def readchar(self) -> int:
        """
        Receive a single character on the bus.

        Return value: The character read, as an integer.  Returns -1 on timeout.
        """
        ...

    def irq(self, *args, **kwargs) -> Incomplete: ...
    def writechar(self, char: int, /) -> None:
        """
        Write a single character on the bus.  ``char`` is an integer to write.
        Return value: ``None``. See note below if CTS flow control is used.
        """
        ...

    @overload
    def read(self) -> bytes | None:
        """
        Read characters.  If ``nbytes`` is specified then read at most that many bytes.
        If ``nbytes`` are available in the buffer, returns immediately, otherwise returns
        when sufficient characters arrive or the timeout elapses.

        If ``nbytes`` is not given then the method reads as much data as possible.  It
        returns after the timeout has elapsed.

        *Note:* for 9 bit characters each character takes two bytes, ``nbytes`` must
        be even, and the number of characters is ``nbytes/2``.

        Return value: a bytes object containing the bytes read in.  Returns ``None``
        on timeout.
        """

    @overload
    def read(self, nbytes: int, /) -> bytes | None:
        """
        Read characters.  If ``nbytes`` is specified then read at most that many bytes.
        If ``nbytes`` are available in the buffer, returns immediately, otherwise returns
        when sufficient characters arrive or the timeout elapses.

        If ``nbytes`` is not given then the method reads as much data as possible.  It
        returns after the timeout has elapsed.

        *Note:* for 9 bit characters each character takes two bytes, ``nbytes`` must
        be even, and the number of characters is ``nbytes/2``.

        Return value: a bytes object containing the bytes read in.  Returns ``None``
        on timeout.
        """

    def deinit(self) -> None:
        """
        Turn off the UART bus.
        """
        ...

    def any(self) -> int:
        """
        Returns the number of bytes waiting (may be 0).
        """
        ...

    def write(self, buf: AnyWritableBuf, /) -> int:
        """
        Write the buffer of bytes to the bus.  If characters are 7 or 8 bits wide
        then each byte is one character.  If characters are 9 bits wide then two
        bytes are used for each character (little endian), and ``buf`` must contain
        an even number of bytes.

        Return value: number of bytes written. If a timeout occurs and no bytes
        were written returns ``None``.
        """
        ...

    @overload
    def readinto(self, buf: AnyWritableBuf, /) -> int | None:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """

    @overload
    def readinto(self, buf: AnyWritableBuf, nbytes: int, /) -> int | None:
        """
        Read bytes into the ``buf``.  If ``nbytes`` is specified then read at most
        that many bytes.  Otherwise, read at most ``len(buf)`` bytes.

        Return value: number of bytes read and stored into ``buf`` or ``None`` on
        timeout.
        """

    def readline(self) -> None:
        """
        Read a line, ending in a newline character. If such a line exists, return is
        immediate. If the timeout elapses, all available data is returned regardless
        of whether a newline exists.

        Return value: the line read or ``None`` on timeout if no data is available.
        """
        ...

    @overload
    def __init__(self, bus: int | str, /):
        """
        Construct a UART object on the given bus.
        For Pyboard ``bus`` can be 1-4, 6, 'XA', 'XB', 'YA', or 'YB'.
        For Pyboard Lite ``bus`` can be 1, 2, 6, 'XB', or 'YA'.
        For Pyboard D ``bus`` can be 1-4, 'XA', 'YA' or 'YB'.
        With no additional parameters, the UART object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.

        The physical pins of the UART buses on Pyboard are:

          - ``UART(4)`` is on ``XA``: ``(TX, RX) = (X1, X2) = (PA0, PA1)``
          - ``UART(1)`` is on ``XB``: ``(TX, RX) = (X9, X10) = (PB6, PB7)``
          - ``UART(6)`` is on ``YA``: ``(TX, RX) = (Y1, Y2) = (PC6, PC7)``
          - ``UART(3)`` is on ``YB``: ``(TX, RX) = (Y9, Y10) = (PB10, PB11)``
          - ``UART(2)`` is on: ``(TX, RX) = (X3, X4) = (PA2, PA3)``

        The Pyboard Lite supports UART(1), UART(2) and UART(6) only, pins are:

          - ``UART(1)`` is on ``XB``: ``(TX, RX) = (X9, X10) = (PB6, PB7)``
          - ``UART(6)`` is on ``YA``: ``(TX, RX) = (Y1, Y2) = (PC6, PC7)``
          - ``UART(2)`` is on: ``(TX, RX) = (X1, X2) = (PA2, PA3)``

        The Pyboard D supports UART(1), UART(2), UART(3) and UART(4) only, pins are:

          - ``UART(4)`` is on ``XA``: ``(TX, RX) = (X1, X2) = (PA0, PA1)``
          - ``UART(1)`` is on ``YA``: ``(TX, RX) = (Y1, Y2) = (PA9, PA10)``
          - ``UART(3)`` is on ``YB``: ``(TX, RX) = (Y9, Y10) = (PB10, PB11)``
          - ``UART(2)`` is on: ``(TX, RX) = (X3, X4) = (PA2, PA3)``

        *Note:* Pyboard D has ``UART(1)`` on ``YA``, unlike Pyboard and Pyboard Lite that both
        have ``UART(1)`` on ``XB`` and ``UART(6)`` on ``YA``.
        """

    @overload
    def __init__(
        self,
        bus: int | str,
        baudrate: int,
        /,
        bits: int = 8,
        parity: int | None = None,
        stop: int = 1,
        *,
        timeout: int = 0,
        flow: int = 0,
        timeout_char: int = 0,
        read_buf_len: int = 64,
    ):
        """
        Construct a UART object on the given bus.
        For Pyboard ``bus`` can be 1-4, 6, 'XA', 'XB', 'YA', or 'YB'.
        For Pyboard Lite ``bus`` can be 1, 2, 6, 'XB', or 'YA'.
        For Pyboard D ``bus`` can be 1-4, 'XA', 'YA' or 'YB'.
        With no additional parameters, the UART object is created but not
        initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.

        The physical pins of the UART buses on Pyboard are:

          - ``UART(4)`` is on ``XA``: ``(TX, RX) = (X1, X2) = (PA0, PA1)``
          - ``UART(1)`` is on ``XB``: ``(TX, RX) = (X9, X10) = (PB6, PB7)``
          - ``UART(6)`` is on ``YA``: ``(TX, RX) = (Y1, Y2) = (PC6, PC7)``
          - ``UART(3)`` is on ``YB``: ``(TX, RX) = (Y9, Y10) = (PB10, PB11)``
          - ``UART(2)`` is on: ``(TX, RX) = (X3, X4) = (PA2, PA3)``

        The Pyboard Lite supports UART(1), UART(2) and UART(6) only, pins are:

          - ``UART(1)`` is on ``XB``: ``(TX, RX) = (X9, X10) = (PB6, PB7)``
          - ``UART(6)`` is on ``YA``: ``(TX, RX) = (Y1, Y2) = (PC6, PC7)``
          - ``UART(2)`` is on: ``(TX, RX) = (X1, X2) = (PA2, PA3)``

        The Pyboard D supports UART(1), UART(2), UART(3) and UART(4) only, pins are:

          - ``UART(4)`` is on ``XA``: ``(TX, RX) = (X1, X2) = (PA0, PA1)``
          - ``UART(1)`` is on ``YA``: ``(TX, RX) = (Y1, Y2) = (PA9, PA10)``
          - ``UART(3)`` is on ``YB``: ``(TX, RX) = (Y9, Y10) = (PB10, PB11)``
          - ``UART(2)`` is on: ``(TX, RX) = (X3, X4) = (PA2, PA3)``

        *Note:* Pyboard D has ``UART(1)`` on ``YA``, unlike Pyboard and Pyboard Lite that both
        have ``UART(1)`` on ``XB`` and ``UART(6)`` on ``YA``.
        """

class USB_HID:
    """
    The USB_HID class allows creation of an object representing the USB
    Human Interface Device (HID) interface.  It can be used to emulate
    a peripheral such as a mouse or keyboard.

    Before you can use this class, you need to use :meth:`pyb.usb_mode()` to set the USB mode to include the HID interface.
    """

    @overload
    def recv(self, data: int, /, *, timeout: int = 5000) -> bytes:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    @overload
    def recv(self, data: AnyWritableBuf, /, *, timeout: int = 5000) -> int:
        """
        Receive data on the bus:

          - ``data`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``data`` is an integer then a new buffer of the bytes received,
        otherwise the number of bytes read into ``data`` is returned.
        """

    def send(self, data: Sequence[int]) -> None:
        """
        Send data over the USB HID interface:

          - ``data`` is the data to send (a tuple/list of integers, or a
            bytearray).
        """
        ...

    def __init__(self) -> None:
        """
        Create a new USB_HID object.
        """

class LED:
    """
    The LED object controls an individual LED (Light Emitting Diode).
    """

    def toggle(self) -> None:
        """
        Toggle the LED between on (maximum intensity) and off.  If the LED is at
        non-zero intensity then it is considered "on" and toggle will turn it off.
        """
        ...

    def on(self) -> None:
        """
        Turn the LED on, to maximum intensity.
        """
        ...

    def off(self) -> None:
        """
        Turn the LED off.
        """
        ...

    @overload
    def intensity(self) -> int:
        """
        Get or set the LED intensity.  Intensity ranges between 0 (off) and 255 (full on).
        If no argument is given, return the LED intensity.
        If an argument is given, set the LED intensity and return ``None``.

        *Note:* Only LED(3) and LED(4) can have a smoothly varying intensity, and
        they use timer PWM to implement it.  LED(3) uses Timer(2) and LED(4) uses
        Timer(3).  These timers are only configured for PWM if the intensity of the
        relevant LED is set to a value between 1 and 254.  Otherwise the timers are
        free for general purpose use.
        """

    @overload
    def intensity(self, value: int, /) -> None:
        """
        Get or set the LED intensity.  Intensity ranges between 0 (off) and 255 (full on).
        If no argument is given, return the LED intensity.
        If an argument is given, set the LED intensity and return ``None``.

        *Note:* Only LED(3) and LED(4) can have a smoothly varying intensity, and
        they use timer PWM to implement it.  LED(3) uses Timer(2) and LED(4) uses
        Timer(3).  These timers are only configured for PWM if the intensity of the
        relevant LED is set to a value between 1 and 254.  Otherwise the timers are
        free for general purpose use.
        """

    def __init__(self, id: int, /) -> None:
        """
        Create an LED object associated with the given LED:

          - ``id`` is the LED number, 1-4.
        """

class RTC:
    """
    The RTC is an independent clock that keeps track of the date
    and time.

    Example usage::

        rtc = pyb.RTC()
        rtc.datetime((2014, 5, 1, 4, 13, 0, 0, 0))
        print(rtc.datetime())
    """

    def info(self) -> int:
        """
        Get information about the startup time and reset source.

         - The lower 0xffff are the number of milliseconds the RTC took to
           start up.
         - Bit 0x10000 is set if a power-on reset occurred.
         - Bit 0x20000 is set if an external reset occurred
        """
        ...

    def init(self, *args, **kwargs) -> Incomplete: ...
    def wakeup(self, timeout: int, callback: Callable[[RTC], None] | None = None, /) -> None:
        """
        Set the RTC wakeup timer to trigger repeatedly at every ``timeout``
        milliseconds.  This trigger can wake the pyboard from both the sleep
        states: :meth:`pyb.stop` and :meth:`pyb.standby`.

        If ``timeout`` is ``None`` then the wakeup timer is disabled.

        If ``callback`` is given then it is executed at every trigger of the
        wakeup timer.  ``callback`` must take exactly one argument.
        """
        ...

    @overload
    def datetime(self, datetimetuple: tuple[int, int, int, int, int, int, int, int], /) -> None:
        """
        Get or set the date and time of the RTC.

        With no arguments, this method returns an 8-tuple with the current
        date and time.  With 1 argument (being an 8-tuple) it sets the date
        and time (and ``subseconds`` is reset to 255).

        The 8-tuple has the following format:

            (year, month, day, weekday, hours, minutes, seconds, subseconds)

        ``weekday`` is 1-7 for Monday through Sunday.

        ``subseconds`` counts down from 255 to 0
        """
        ...

    @overload
    def datetime(self, /) -> Tuple:
        """
        Get or set the date and time of the RTC.

        With no arguments, this method returns an 8-tuple with the current
        date and time.  With 1 argument (being an 8-tuple) it sets the date
        and time (and ``subseconds`` is reset to 255).

        The 8-tuple has the following format:

            (year, month, day, weekday, hours, minutes, seconds, subseconds)

        ``weekday`` is 1-7 for Monday through Sunday.

        ``subseconds`` counts down from 255 to 0
        """
        ...

    @overload
    def calibration(self) -> int:
        """
        Get or set RTC calibration.

        With no arguments, ``calibration()`` returns the current calibration
        value, which is an integer in the range [-511 : 512].  With one
        argument it sets the RTC calibration.

        The RTC Smooth Calibration mechanism adjusts the RTC clock rate by
        adding or subtracting the given number of ticks from the 32768 Hz
        clock over a 32 second period (corresponding to 2^20 clock ticks.)
        Each tick added will speed up the clock by 1 part in 2^20, or 0.954
        ppm; likewise the RTC clock it slowed by negative values. The
        usable calibration range is:
        (-511 * 0.954) ~= -487.5 ppm up to (512 * 0.954) ~= 488.5 ppm
        """

    @overload
    def calibration(self, cal: int, /) -> None:
        """
        Get or set RTC calibration.

        With no arguments, ``calibration()`` returns the current calibration
        value, which is an integer in the range [-511 : 512].  With one
        argument it sets the RTC calibration.

        The RTC Smooth Calibration mechanism adjusts the RTC clock rate by
        adding or subtracting the given number of ticks from the 32768 Hz
        clock over a 32 second period (corresponding to 2^20 clock ticks.)
        Each tick added will speed up the clock by 1 part in 2^20, or 0.954
        ppm; likewise the RTC clock it slowed by negative values. The
        usable calibration range is:
        (-511 * 0.954) ~= -487.5 ppm up to (512 * 0.954) ~= 488.5 ppm
        """

    def __init__(self) -> None:
        """
        Create an RTC object.
        """

class Pin:
    """
    A pin is the basic object to control I/O pins.  It has methods to set
    the mode of the pin (input, output, etc) and methods to get and set the
    digital logic level. For analog control of a pin, see the ADC class.

    Usage Model:

    All Board Pins are predefined as pyb.Pin.board.Name::

        x1_pin = pyb.Pin.board.X1

        g = pyb.Pin(pyb.Pin.board.X1, pyb.Pin.IN)

    CPU pins which correspond to the board pins are available
    as ``pyb.Pin.cpu.Name``. For the CPU pins, the names are the port letter
    followed by the pin number. On the PYBv1.0, ``pyb.Pin.board.X1`` and
    ``pyb.Pin.cpu.A0`` are the same pin.

    You can also use strings::

        g = pyb.Pin('X1', pyb.Pin.OUT_PP)

    Users can add their own names::

        MyMapperDict = { 'LeftMotorDir' : pyb.Pin.cpu.C12 }
        pyb.Pin.dict(MyMapperDict)
        g = pyb.Pin("LeftMotorDir", pyb.Pin.OUT_OD)

    and can query mappings::

        pin = pyb.Pin("LeftMotorDir")

    Users can also add their own mapping function::

        def MyMapper(pin_name):
           if pin_name == "LeftMotorDir":
               return pyb.Pin.cpu.A0

        pyb.Pin.mapper(MyMapper)

    So, if you were to call: ``pyb.Pin("LeftMotorDir", pyb.Pin.OUT_PP)``
    then ``"LeftMotorDir"`` is passed directly to the mapper function.

    To summarise, the following order determines how things get mapped into
    an ordinal pin number:

    1. Directly specify a pin object
    2. User supplied mapping function
    3. User supplied mapping (object must be usable as a dictionary key)
    4. Supply a string which matches a board pin
    5. Supply a string which matches a CPU port/pin

    You can set ``pyb.Pin.debug(True)`` to get some debug information about
    how a particular object gets mapped to a pin.

    When a pin has the ``Pin.PULL_UP`` or ``Pin.PULL_DOWN`` pull-mode enabled,
    that pin has an effective 40k Ohm resistor pulling it to 3V3 or GND
    respectively (except pin Y5 which has 11k Ohm resistors).

    Now every time a falling edge is seen on the gpio pin, the callback will be
    executed. Caution: mechanical push buttons have "bounce" and pushing or
    releasing a switch will often generate multiple edges.
    See: http://www.eng.utah.edu/~cs5780/debouncing.pdf for a detailed
    explanation, along with various techniques for debouncing.

    All pin objects go through the pin mapper to come up with one of the
    gpio pins.
    """

    AF_OD: Final[int] = 18
    AF9_TIM14: Final[int] = 9
    ALT_OPEN_DRAIN: Final[int] = 18
    AF_PP: Final[int] = 2
    ALT: Final[int] = 2
    AF9_CAN1: Final[int] = 9
    AF8_USART6: Final[int] = 8
    AF9_TIM13: Final[int] = 9
    AF9_CAN2: Final[int] = 9
    AF9_TIM12: Final[int] = 9
    PULL_UP: Final[int] = 1
    OUT_PP: Final[int] = 1
    OUT_OD: Final[int] = 17
    ANALOG: Final[int] = 3
    PULL_DOWN: Final[int] = 2
    PULL_NONE: Final[int] = 0
    IRQ_FALLING: Final[int] = 270598144
    IN: Final[int] = 0
    OUT: Final[int] = 1
    IRQ_RISING: Final[int] = 269549568
    OPEN_DRAIN: Final[int] = 17
    AF2_TIM5: Final[int] = 2
    AF3_TIM10: Final[int] = 3
    AF3_TIM11: Final[int] = 3
    AF3_TIM8: Final[int] = 3
    AF3_TIM9: Final[int] = 3
    AF2_TIM4: Final[int] = 2
    AF1_TIM1: Final[int] = 1
    AF1_TIM2: Final[int] = 1
    AF2_TIM3: Final[int] = 2
    AF8_UART4: Final[int] = 8
    AF6_I2S2: Final[int] = 6
    AF7_USART1: Final[int] = 7
    AF7_USART2: Final[int] = 7
    AF7_USART3: Final[int] = 7
    AF4_I2C1: Final[int] = 4
    AF5_SPI2: Final[int] = 5
    AF4_I2C2: Final[int] = 4
    AF5_I2S2: Final[int] = 5
    AF5_SPI1: Final[int] = 5
    def mode(self) -> int:
        """
        Returns the currently configured mode of the pin. The integer returned
        will match one of the allowed constants for the mode argument to the init
        function.
        """
        ...

    def name(self) -> str:
        """
        Get the pin name.
        """
        ...

    def pull(self) -> int:
        """
        Returns the currently configured pull of the pin. The integer returned
        will match one of the allowed constants for the pull argument to the init
        function.
        """
        ...

    def low(self, *args, **kwargs) -> Incomplete: ...
    def irq(self, *args, **kwargs) -> Incomplete: ...
    def pin(self) -> int:
        """
        Get the pin number.
        """
        ...

    def port(self) -> int:
        """
        Get the pin port.
        """
        ...

    def names(self) -> str:
        """
        Returns the cpu and board names for this pin.
        """
        ...

    def on(self, *args, **kwargs) -> Incomplete: ...
    def off(self, *args, **kwargs) -> Incomplete: ...
    def init(
        self,
        mode: int = IN,
        pull: int = PULL_NONE,
        *,
        value: Any = None,
        alt: str | int = -1,
    ) -> None:
        """
        Initialise the pin:

          - *mode* can be one of:

             - ``Pin.IN`` - configure the pin for input;
             - ``Pin.OUT_PP`` - configure the pin for output, with push-pull control;
             - ``Pin.OUT_OD`` - configure the pin for output, with open-drain control;
             - ``Pin.ALT`` - configure the pin for alternate function, input or output;
             - ``Pin.AF_PP`` - configure the pin for alternate function, push-pull;
             - ``Pin.AF_OD`` - configure the pin for alternate function, open-drain;
             - ``Pin.ANALOG`` - configure the pin for analog.

          - *pull* can be one of:

             - ``Pin.PULL_NONE`` - no pull up or down resistors;
             - ``Pin.PULL_UP`` - enable the pull-up resistor;
             - ``Pin.PULL_DOWN`` - enable the pull-down resistor.

            When a pin has the ``Pin.PULL_UP`` or ``Pin.PULL_DOWN`` pull-mode enabled,
            that pin has an effective 40k Ohm resistor pulling it to 3V3 or GND
            respectively (except pin Y5 which has 11k Ohm resistors).

          - *value* if not None will set the port output value before enabling the pin.

          - *alt* can be used when mode is ``Pin.ALT`` , ``Pin.AF_PP`` or ``Pin.AF_OD`` to
            set the index or name of one of the alternate functions associated with a pin.
            This arg was previously called *af* which can still be used if needed.

        Returns: ``None``.
        """
        ...

    def af_list(self) -> List:
        """
        Returns an array of alternate functions available for this pin.
        """
        ...

    def af(self) -> int:
        """
        Returns the currently configured alternate-function of the pin. The
        integer returned will match one of the allowed constants for the af
        argument to the init function.
        """
        ...

    @overload
    def value(self) -> int:
        """
        Get or set the digital logic level of the pin:

          - With no argument, return 0 or 1 depending on the logic level of the pin.
          - With ``value`` given, set the logic level of the pin.  ``value`` can be
            anything that converts to a boolean.  If it converts to ``True``, the pin
            is set high, otherwise it is set low.
        """

    @overload
    def value(self, value: Any, /) -> None:
        """
        Get or set the digital logic level of the pin:

          - With no argument, return 0 or 1 depending on the logic level of the pin.
          - With ``value`` given, set the logic level of the pin.  ``value`` can be
            anything that converts to a boolean.  If it converts to ``True``, the pin
            is set high, otherwise it is set low.
        """

    def high(self, *args, **kwargs) -> Incomplete: ...
    def gpio(self) -> int:
        """
        Returns the base address of the GPIO block associated with this pin.
        """
        ...

    @overload
    @staticmethod
    def dict() -> Dict[str, Pin]:
        """
        Get or set the pin mapper dictionary.
        """

    @overload
    @staticmethod
    def dict(dict: Dict[str, Pin], /) -> None:
        """
        Get or set the pin mapper dictionary.
        """

    @overload
    @staticmethod
    def debug() -> bool:
        """
        Get or set the debugging state (``True`` or ``False`` for on or off).
        """

    @overload
    @staticmethod
    def debug(state: bool, /) -> None:
        """
        Get or set the debugging state (``True`` or ``False`` for on or off).
        """

    class cpu:
        B9: Pin  ## = Pin(Pin.cpu.B9, mode=Pin.IN)
        B8: Pin  ## = Pin(Pin.cpu.B8, mode=Pin.IN)
        B7: Pin  ## = Pin(Pin.cpu.B7, mode=Pin.IN)
        C0: Pin  ## = Pin(Pin.cpu.C0, mode=Pin.IN)
        C1: Pin  ## = Pin(Pin.cpu.C1, mode=Pin.IN)
        C10: Pin  ## = Pin(Pin.cpu.C10, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        B3: Pin  ## = Pin(Pin.cpu.B3, mode=Pin.IN, pull=Pin.PULL_UP)
        B2: Pin  ## = Pin(Pin.cpu.B2, mode=Pin.IN)
        B6: Pin  ## = Pin(Pin.cpu.B6, mode=Pin.IN)
        B4: Pin  ## = Pin(Pin.cpu.B4, mode=Pin.OUT)
        B5: Pin  ## = Pin(Pin.cpu.B5, mode=Pin.OUT)
        B15: Pin  ## = Pin(Pin.cpu.B15, mode=Pin.IN)
        C7: Pin  ## = Pin(Pin.cpu.C7, mode=Pin.IN)
        C6: Pin  ## = Pin(Pin.cpu.C6, mode=Pin.IN)
        C5: Pin  ## = Pin(Pin.cpu.C5, mode=Pin.IN)
        C8: Pin  ## = Pin(Pin.cpu.C8, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        C9: Pin  ## = Pin(Pin.cpu.C9, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        C11: Pin  ## = Pin(Pin.cpu.C11, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        C13: Pin  ## = Pin(Pin.cpu.C13, mode=Pin.IN)
        C12: Pin  ## = Pin(Pin.cpu.C12, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        C4: Pin  ## = Pin(Pin.cpu.C4, mode=Pin.IN)
        C2: Pin  ## = Pin(Pin.cpu.C2, mode=Pin.IN)
        C3: Pin  ## = Pin(Pin.cpu.C3, mode=Pin.IN)
        D2: Pin  ## = Pin(Pin.cpu.D2, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        A15: Pin  ## = Pin(Pin.cpu.A15, mode=Pin.OUT)
        A14: Pin  ## = Pin(Pin.cpu.A14, mode=Pin.OUT)
        A13: Pin  ## = Pin(Pin.cpu.A13, mode=Pin.OUT)
        A2: Pin  ## = Pin(Pin.cpu.A2, mode=Pin.IN)
        A3: Pin  ## = Pin(Pin.cpu.A3, mode=Pin.IN)
        A4: Pin  ## = Pin(Pin.cpu.A4, mode=Pin.IN)
        A1: Pin  ## = Pin(Pin.cpu.A1, mode=Pin.IN)
        A0: Pin  ## = Pin(Pin.cpu.A0, mode=Pin.IN)
        A12: Pin  ## = Pin(Pin.cpu.A12, mode=Pin.ALT, alt=10)
        A10: Pin  ## = Pin(Pin.cpu.A10, mode=Pin.ALT_OPEN_DRAIN, pull=Pin.PULL_UP, alt=10)
        A11: Pin  ## = Pin(Pin.cpu.A11, mode=Pin.ALT, alt=10)
        B14: Pin  ## = Pin(Pin.cpu.B14, mode=Pin.IN)
        B11: Pin  ## = Pin(Pin.cpu.B11, mode=Pin.IN)
        B10: Pin  ## = Pin(Pin.cpu.B10, mode=Pin.IN)
        B1: Pin  ## = Pin(Pin.cpu.B1, mode=Pin.IN)
        B12: Pin  ## = Pin(Pin.cpu.B12, mode=Pin.IN)
        B13: Pin  ## = Pin(Pin.cpu.B13, mode=Pin.IN)
        A5: Pin  ## = Pin(Pin.cpu.A5, mode=Pin.IN)
        A7: Pin  ## = Pin(Pin.cpu.A7, mode=Pin.IN)
        A6: Pin  ## = Pin(Pin.cpu.A6, mode=Pin.IN)
        B0: Pin  ## = Pin(Pin.cpu.B0, mode=Pin.IN)
        A8: Pin  ## = Pin(Pin.cpu.A8, mode=Pin.IN, pull=Pin.PULL_UP)
        A9: Pin  ## = Pin(Pin.cpu.A9, mode=Pin.IN)
        def __init__(self, *argv, **kwargs) -> None: ...

    @overload
    @staticmethod
    def mapper() -> Callable[[str], Pin]:
        """
        Get or set the pin mapper function.
        """

    @overload
    @staticmethod
    def mapper(fun: Callable[[str], Pin], /) -> None:
        """
        Get or set the pin mapper function.
        """

    class board:
        X5: Pin  ## = Pin(Pin.cpu.A4, mode=Pin.IN)
        X18: Pin  ## = Pin(Pin.cpu.C13, mode=Pin.IN)
        X4: Pin  ## = Pin(Pin.cpu.A3, mode=Pin.IN)
        X8: Pin  ## = Pin(Pin.cpu.A7, mode=Pin.IN)
        X6: Pin  ## = Pin(Pin.cpu.A5, mode=Pin.IN)
        X7: Pin  ## = Pin(Pin.cpu.A6, mode=Pin.IN)
        X2: Pin  ## = Pin(Pin.cpu.A1, mode=Pin.IN)
        X3: Pin  ## = Pin(Pin.cpu.A2, mode=Pin.IN)
        X19: Pin  ## = Pin(Pin.cpu.C0, mode=Pin.IN)
        X22: Pin  ## = Pin(Pin.cpu.C3, mode=Pin.IN)
        X20: Pin  ## = Pin(Pin.cpu.C1, mode=Pin.IN)
        X21: Pin  ## = Pin(Pin.cpu.C2, mode=Pin.IN)
        Y5: Pin  ## = Pin(Pin.cpu.B12, mode=Pin.IN)
        X9: Pin  ## = Pin(Pin.cpu.B6, mode=Pin.IN)
        Y4: Pin  ## = Pin(Pin.cpu.B9, mode=Pin.IN)
        Y8: Pin  ## = Pin(Pin.cpu.B15, mode=Pin.IN)
        Y6: Pin  ## = Pin(Pin.cpu.B13, mode=Pin.IN)
        Y7: Pin  ## = Pin(Pin.cpu.B14, mode=Pin.IN)
        Y10: Pin  ## = Pin(Pin.cpu.B11, mode=Pin.IN)
        Y3: Pin  ## = Pin(Pin.cpu.B8, mode=Pin.IN)
        Y1: Pin  ## = Pin(Pin.cpu.C6, mode=Pin.IN)
        Y2: Pin  ## = Pin(Pin.cpu.C7, mode=Pin.IN)
        Y11: Pin  ## = Pin(Pin.cpu.B0, mode=Pin.IN)
        Y12: Pin  ## = Pin(Pin.cpu.B1, mode=Pin.IN)
        Y9: Pin  ## = Pin(Pin.cpu.B10, mode=Pin.IN)
        SD_CK: Pin  ## = Pin(Pin.cpu.C12, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        X17: Pin  ## = Pin(Pin.cpu.B3, mode=Pin.IN, pull=Pin.PULL_UP)
        SD: Pin  ## = Pin(Pin.cpu.A8, mode=Pin.IN, pull=Pin.PULL_UP)
        SD_D1: Pin  ## = Pin(Pin.cpu.C9, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        SD_CMD: Pin  ## = Pin(Pin.cpu.D2, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        SD_D0: Pin  ## = Pin(Pin.cpu.C8, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        LED_GREEN: Pin  ## = Pin(Pin.cpu.A14, mode=Pin.OUT)
        MMA_INT: Pin  ## = Pin(Pin.cpu.B2, mode=Pin.IN)
        LED_BLUE: Pin  ## = Pin(Pin.cpu.B4, mode=Pin.OUT)
        MMA_AVDD: Pin  ## = Pin(Pin.cpu.B5, mode=Pin.OUT)
        LED_RED: Pin  ## = Pin(Pin.cpu.A13, mode=Pin.OUT)
        LED_YELLOW: Pin  ## = Pin(Pin.cpu.A15, mode=Pin.OUT)
        X1: Pin  ## = Pin(Pin.cpu.A0, mode=Pin.IN)
        SD_D2: Pin  ## = Pin(Pin.cpu.C10, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        USB_VBUS: Pin  ## = Pin(Pin.cpu.A9, mode=Pin.IN)
        X12: Pin  ## = Pin(Pin.cpu.C5, mode=Pin.IN)
        X10: Pin  ## = Pin(Pin.cpu.B7, mode=Pin.IN)
        X11: Pin  ## = Pin(Pin.cpu.C4, mode=Pin.IN)
        SD_SW: Pin  ## = Pin(Pin.cpu.A8, mode=Pin.IN, pull=Pin.PULL_UP)
        USB_ID: Pin  ## = Pin(Pin.cpu.A10, mode=Pin.ALT_OPEN_DRAIN, pull=Pin.PULL_UP, alt=10)
        SD_D3: Pin  ## = Pin(Pin.cpu.C11, mode=Pin.ALT, pull=Pin.PULL_UP, alt=12)
        USB_DP: Pin  ## = Pin(Pin.cpu.A12, mode=Pin.ALT, alt=10)
        SW: Pin  ## = Pin(Pin.cpu.B3, mode=Pin.IN, pull=Pin.PULL_UP)
        USB_DM: Pin  ## = Pin(Pin.cpu.A11, mode=Pin.ALT, alt=10)
        def __init__(self, *argv, **kwargs) -> None: ...

    def __init__(
        self,
        id: Pin | str | int,
        /,
        mode: int = IN,
        pull: int = PULL_NONE,
        *,
        value: Any = None,
        alt: str | int = -1,
    ) -> None:
        """
        Create a new Pin object associated with the id.  If additional arguments are given,
        they are used to initialise the pin.  See :meth:`pin.init`.
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

class SPI:
    """
    SPI is a serial protocol that is driven by a controller.  At the physical level
    there are 3 lines: SCK, MOSI, MISO.

    See usage model of I2C; SPI is very similar.  Main difference is
    parameters to init the SPI bus::

        from pyb import SPI
        spi = SPI(1, SPI.CONTROLLER, baudrate=600000, polarity=1, phase=0, crc=0x7)

    Only required parameter is mode, SPI.CONTROLLER or SPI.PERIPHERAL.  Polarity can be
    0 or 1, and is the level the idle clock line sits at.  Phase can be 0 or 1
    to sample data on the first or second clock edge respectively.  Crc can be
    None for no CRC, or a polynomial specifier.

    Additional methods for SPI::

        data = spi.send_recv(b'1234')        # send 4 bytes and receive 4 bytes
        buf = bytearray(4)
        spi.send_recv(b'1234', buf)          # send 4 bytes and receive 4 into buf
        spi.send_recv(buf, buf)              # send/recv 4 bytes from/to buf
    """

    MASTER: Final[int] = 260
    LSB: Final[int] = 128
    SLAVE: Final[int] = 0
    MSB: Final[int] = 0
    PERIPHERAL: Final[int] = 0
    CONTROLLER: Final[int] = 260
    def deinit(self) -> None:
        """
        Turn off the SPI bus.
        """
        ...

    def send_recv(
        self,
        send: int | AnyWritableBuf,
        recv: AnyWritableBuf | None = None,
        /,
        *,
        timeout: int = 5000,
    ) -> bytes:
        """
        Send and receive data on the bus at the same time:

          - ``send`` is the data to send (an integer to send, or a buffer object).
          - ``recv`` is a mutable buffer which will be filled with received bytes.
            It can be the same as ``send``, or omitted.  If omitted, a new buffer will
            be created.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: the buffer with the received bytes.
        """
        ...

    def recv(self, recv: int | AnyWritableBuf, /, *, timeout: int = 5000) -> bytes:
        """
        Receive data on the bus:

          - ``recv`` can be an integer, which is the number of bytes to receive,
            or a mutable buffer, which will be filled with received bytes.
          - ``timeout`` is the timeout in milliseconds to wait for the receive.

        Return value: if ``recv`` is an integer then a new buffer of the bytes received,
        otherwise the same buffer that was passed in to ``recv``.
        """
        ...

    @overload
    def init(
        self,
        mode: int = CONTROLLER,
        baudrate: int = 328125,
        *,
        polarity: int = 1,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        ti: bool = False,
        crc: int | None = None,
    ):
        """
        Initialise the SPI bus with the given parameters:

          - ``mode`` must be either ``SPI.CONTROLLER`` or ``SPI.PERIPHERAL``.
          - ``baudrate`` is the SCK clock rate (only sensible for a controller).
          - ``prescaler`` is the prescaler to use to derive SCK from the APB bus frequency;
            use of ``prescaler`` overrides ``baudrate``.
          - ``polarity`` can be 0 or 1, and is the level the idle clock line sits at.
          - ``phase`` can be 0 or 1 to sample data on the first or second clock edge
            respectively.
          - ``bits`` can be 8 or 16, and is the number of bits in each transferred word.
          - ``firstbit`` can be ``SPI.MSB`` or ``SPI.LSB``.
          - ``ti`` True indicates Texas Instruments, as opposed to Motorola, signal conventions.
          - ``crc`` can be None for no CRC, or a polynomial specifier.

        Note that the SPI clock frequency will not always be the requested baudrate.
        The hardware only supports baudrates that are the APB bus frequency
        (see :meth:`pyb.freq`) divided by a prescaler, which can be 2, 4, 8, 16, 32,
        64, 128 or 256.  SPI(1) is on AHB2, and SPI(2) is on AHB1.  For precise
        control over the SPI clock frequency, specify ``prescaler`` instead of
        ``baudrate``.

        Printing the SPI object will show you the computed baudrate and the chosen
        prescaler.
        """

    @overload
    def init(
        self,
        mode: int = CONTROLLER,
        *,
        prescaler: int = 256,
        polarity: int = 1,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        ti: bool = False,
        crc: int | None = None,
    ):
        """
        Initialise the SPI bus with the given parameters:

          - ``mode`` must be either ``SPI.CONTROLLER`` or ``SPI.PERIPHERAL``.
          - ``baudrate`` is the SCK clock rate (only sensible for a controller).
          - ``prescaler`` is the prescaler to use to derive SCK from the APB bus frequency;
            use of ``prescaler`` overrides ``baudrate``.
          - ``polarity`` can be 0 or 1, and is the level the idle clock line sits at.
          - ``phase`` can be 0 or 1 to sample data on the first or second clock edge
            respectively.
          - ``bits`` can be 8 or 16, and is the number of bits in each transferred word.
          - ``firstbit`` can be ``SPI.MSB`` or ``SPI.LSB``.
          - ``ti`` True indicates Texas Instruments, as opposed to Motorola, signal conventions.
          - ``crc`` can be None for no CRC, or a polynomial specifier.

        Note that the SPI clock frequency will not always be the requested baudrate.
        The hardware only supports baudrates that are the APB bus frequency
        (see :meth:`pyb.freq`) divided by a prescaler, which can be 2, 4, 8, 16, 32,
        64, 128 or 256.  SPI(1) is on AHB2, and SPI(2) is on AHB1.  For precise
        control over the SPI clock frequency, specify ``prescaler`` instead of
        ``baudrate``.

        Printing the SPI object will show you the computed baudrate and the chosen
        prescaler.
        """

    def write_readinto(self, *args, **kwargs) -> Incomplete: ...
    def write(self, *args, **kwargs) -> Incomplete: ...
    def read(self, *args, **kwargs) -> Incomplete: ...
    def readinto(self, *args, **kwargs) -> Incomplete: ...
    def send(self, send: int | AnyWritableBuf | bytes, /, *, timeout: int = 5000) -> None:
        """
        Send data on the bus:

          - ``send`` is the data to send (an integer to send, or a buffer object).
          - ``timeout`` is the timeout in milliseconds to wait for the send.

        Return value: ``None``.
        """
        ...

    @overload
    def __init__(self, bus: int, /):
        """
        Construct an SPI object on the given bus.  ``bus`` can be 1 or 2, or
        'X' or 'Y'. With no additional parameters, the SPI object is created but
        not initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.

        The physical pins of the SPI buses are:

          - ``SPI(1)`` is on the X position: ``(NSS, SCK, MISO, MOSI) = (X5, X6, X7, X8) = (PA4, PA5, PA6, PA7)``
          - ``SPI(2)`` is on the Y position: ``(NSS, SCK, MISO, MOSI) = (Y5, Y6, Y7, Y8) = (PB12, PB13, PB14, PB15)``

        At the moment, the NSS pin is not used by the SPI driver and is free
        for other use.
        """

    @overload
    def __init__(
        self,
        bus: int,
        /,
        mode: int = CONTROLLER,
        baudrate: int = 328125,
        *,
        polarity: int = 1,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        ti: bool = False,
        crc: int | None = None,
    ):
        """
        Construct an SPI object on the given bus.  ``bus`` can be 1 or 2, or
        'X' or 'Y'. With no additional parameters, the SPI object is created but
        not initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.

        The physical pins of the SPI buses are:

          - ``SPI(1)`` is on the X position: ``(NSS, SCK, MISO, MOSI) = (X5, X6, X7, X8) = (PA4, PA5, PA6, PA7)``
          - ``SPI(2)`` is on the Y position: ``(NSS, SCK, MISO, MOSI) = (Y5, Y6, Y7, Y8) = (PB12, PB13, PB14, PB15)``

        At the moment, the NSS pin is not used by the SPI driver and is free
        for other use.
        """

    @overload
    def __init__(
        self,
        bus: int,
        /,
        mode: int = CONTROLLER,
        *,
        prescaler: int = 256,
        polarity: int = 1,
        phase: int = 0,
        bits: int = 8,
        firstbit: int = MSB,
        ti: bool = False,
        crc: int | None = None,
    ):
        """
        Construct an SPI object on the given bus.  ``bus`` can be 1 or 2, or
        'X' or 'Y'. With no additional parameters, the SPI object is created but
        not initialised (it has the settings from the last initialisation of
        the bus, if any).  If extra arguments are given, the bus is initialised.
        See ``init`` for parameters of initialisation.

        The physical pins of the SPI buses are:

          - ``SPI(1)`` is on the X position: ``(NSS, SCK, MISO, MOSI) = (X5, X6, X7, X8) = (PA4, PA5, PA6, PA7)``
          - ``SPI(2)`` is on the Y position: ``(NSS, SCK, MISO, MOSI) = (Y5, Y6, Y7, Y8) = (PB12, PB13, PB14, PB15)``

        At the moment, the NSS pin is not used by the SPI driver and is free
        for other use.
        """

SD: Incomplete  ## <class 'SDCard'> = <SDCard>

class SDCard:
    def writeblocks(self, *args, **kwargs) -> Incomplete: ...
    def power(self, *args, **kwargs) -> Incomplete: ...
    def present(self, *args, **kwargs) -> Incomplete: ...
    def readblocks(self, *args, **kwargs) -> Incomplete: ...
    def ioctl(self, *args, **kwargs) -> Incomplete: ...
    def read(self, *args, **kwargs) -> Incomplete: ...
    def write(self, *args, **kwargs) -> Incomplete: ...
    def info(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...

class timerchannel:
    @overload
    @abstractmethod
    def capture(self) -> int:
        """
        Get or set the capture value associated with a channel.
        capture, compare, and pulse_width are all aliases for the same function.
        capture is the logical name to use when the channel is in input capture mode.
        """

    @overload
    @abstractmethod
    def capture(self, value: int, /) -> None:
        """
        Get or set the capture value associated with a channel.
        capture, compare, and pulse_width are all aliases for the same function.
        capture is the logical name to use when the channel is in input capture mode.
        """

    @overload
    @abstractmethod
    def compare(self) -> int:
        """
        Get or set the compare value associated with a channel.
        capture, compare, and pulse_width are all aliases for the same function.
        compare is the logical name to use when the channel is in output compare mode.
        """

    @overload
    @abstractmethod
    def compare(self, value: int, /) -> None:
        """
        Get or set the compare value associated with a channel.
        capture, compare, and pulse_width are all aliases for the same function.
        compare is the logical name to use when the channel is in output compare mode.
        """

    @overload
    @abstractmethod
    def pulse_width(self) -> int:
        """
        Get or set the pulse width value associated with a channel.
        capture, compare, and pulse_width are all aliases for the same function.
        pulse_width is the logical name to use when the channel is in PWM mode.

        In edge aligned mode, a pulse_width of ``period + 1`` corresponds to a duty cycle of 100%
        In center aligned mode, a pulse width of ``period`` corresponds to a duty cycle of 100%
        """

    @overload
    @abstractmethod
    def pulse_width(self, value: int, /) -> None:
        """
        Get or set the pulse width value associated with a channel.
        capture, compare, and pulse_width are all aliases for the same function.
        pulse_width is the logical name to use when the channel is in PWM mode.

        In edge aligned mode, a pulse_width of ``period + 1`` corresponds to a duty cycle of 100%
        In center aligned mode, a pulse width of ``period`` corresponds to a duty cycle of 100%
        """

    @overload
    @abstractmethod
    def pulse_width_percent(self) -> float:
        """
        Get or set the pulse width percentage associated with a channel.  The value
        is a number between 0 and 100 and sets the percentage of the timer period
        for which the pulse is active.  The value can be an integer or
        floating-point number for more accuracy.  For example, a value of 25 gives
        a duty cycle of 25%.
        """

    @overload
    @abstractmethod
    def pulse_width_percent(self, value: int | float, /) -> None:
        """
        Get or set the pulse width percentage associated with a channel.  The value
        is a number between 0 and 100 and sets the percentage of the timer period
        for which the pulse is active.  The value can be an integer or
        floating-point number for more accuracy.  For example, a value of 25 gives
        a duty cycle of 25%.
        """
