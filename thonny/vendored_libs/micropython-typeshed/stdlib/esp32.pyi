"""
Functionality specific to the ESP32.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/esp32.html

The ``esp32`` module contains functions and classes specifically aimed at
controlling ESP32 modules.

---
Module: 'esp32' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import Any, List, Optional, Sequence, Tuple, overload, Final
from _typeshed import Incomplete
from _mpy_shed import AnyReadableBuf
from machine import Pin
from typing_extensions import Awaitable, TypeAlias, TypeVar
from vfs import AbstractBlockDev

WAKEUP_ALL_LOW: Final[bool] = False
WAKEUP_ANY_HIGH: Final[bool] = True
HEAP_EXEC: Final[int] = 1
HEAP_DATA: Final[int] = 4

def raw_temperature() -> int:
    """
    Read the raw value of the internal temperature sensor, returning an integer.
    """
    ...

def idf_heap_info(capabilities: int) -> List[Tuple]:
    """
    Returns information about the ESP-IDF heap memory regions. One of them contains
    the MicroPython heap and the others are used by ESP-IDF, e.g., for network
    buffers and other data. This data is useful to get a sense of how much memory
    is available to ESP-IDF and the networking stack in particular. It may shed
    some light on situations where ESP-IDF operations fail due to allocation failures.

    The capabilities parameter corresponds to ESP-IDF's ``MALLOC_CAP_XXX`` values but the
    two most useful ones are predefined as `esp32.HEAP_DATA` for data heap regions and
    `esp32.HEAP_EXEC` for executable regions as used by the native code emitter.

    The return value is a list of 4-tuples, where each 4-tuple corresponds to one heap
    and contains: the total bytes, the free bytes, the largest free block, and
    the minimum free seen over time.

    Example after booting::

        >>> import esp32; esp32.idf_heap_info(esp32.HEAP_DATA)
        [(240, 0, 0, 0), (7288, 0, 0, 0), (16648, 4, 4, 4), (79912, 35712, 35512, 35108),
         (15072, 15036, 15036, 15036), (113840, 0, 0, 0)]

    ``Note:`` Free IDF heap memory in the `esp32.HEAP_DATA` region is available
       to be automatically added to the MicroPython heap to prevent a
       MicroPython allocation from failing. However, the information returned
       here is otherwise *not* useful to troubleshoot Python allocation
       failures. :func:`micropython.mem_info()` and :func:`gc.mem_free()` should
       be used instead:

       The "max new split" value in :func:`micropython.mem_info()` output
       corresponds to the largest free block of ESP-IDF heap that could be
       automatically added on demand to the MicroPython heap.

       The result of :func:`gc.mem_free()` is the total of the current "free"
       and "max new split" values printed by :func:`micropython.mem_info()`.
    """
    ...

def wake_on_touch(wake: bool, /) -> None:
    """
    Configure whether or not a touch will wake the device from sleep.
    *wake* should be a boolean value.
    """
    ...

def wake_on_ext0(pin: Pin | None, level: int, /) -> None:
    """
    Configure how EXT0 wakes the device from sleep.  *pin* can be ``None``
    or a valid Pin object.  *level* should be ``esp32.WAKEUP_ALL_LOW`` or
    ``esp32.WAKEUP_ANY_HIGH``.
    """
    ...

def wake_on_ext1(pins: List[Pin] | Tuple[Pin, ...] | None, level: int, /) -> None:
    """
    Configure how EXT1 wakes the device from sleep.  *pins* can be ``None``
    or a tuple/list of valid Pin objects.  *level* should be ``esp32.WAKEUP_ALL_LOW``
    or ``esp32.WAKEUP_ANY_HIGH``.
    """
    ...

def wake_on_ulp(wake) -> None:
    """
    Configure whether or not the Ultra-Low-Power co-processor can wake the
    device from sleep. *wake* should be a boolean value.
    """
    ...

def gpio_deep_sleep_hold(enable) -> None:
    """
    Configure whether non-RTC GPIO pin configuration is retained during
    deep-sleep mode for held pads. *enable* should be a boolean value.
    """
    ...

class ULP:
    """
    This class provides access to the Ultra-Low-Power co-processor.
    """

    RESERVE_MEM: Final[int] = 2040
    def run(self, entry_point: int, /) -> None:
        """
        Start the ULP running at the given *entry_point*.
        """
        ...

    def set_wakeup_period(self, period_index: int, period_us: int, /) -> None:
        """
        Set the wake-up period.
        """
        ...

    def load_binary(self, load_addr: int, program_binary: AnyReadableBuf, /) -> None:
        """
        Load a *program_binary* into the ULP at the given *load_addr*.
        """
        ...

    def __init__(self) -> None:
        """
        This class provides access to the Ultra-Low-Power co-processor.
        """

class NVS:
    """
    This class gives access to the Non-Volatile storage managed by ESP-IDF. The NVS is partitioned
    into namespaces and each namespace contains typed key-value pairs. The keys are strings and the
    values may be various integer types, strings, and binary blobs. The driver currently only
    supports 32-bit signed integers and blobs.

    .. warning::

        Changes to NVS need to be committed to flash by calling the commit method. Failure
        to call commit results in changes being lost at the next reset.
    """

    def get_i32(self, key: str, /) -> int:
        """
        Returns the signed integer value for the specified key. Raises an OSError if the key does not
        exist or has a different type.
        """
        ...

    def set_i32(self, key: str, value: int, /) -> None:
        """
        Sets a 32-bit signed integer value for the specified key. Remember to call *commit*!
        """
        ...

    def set_blob(self, key: str, value: AnyReadableBuf, /) -> None:
        """
        Sets a binary blob value for the specified key. The value passed in must support the buffer
        protocol, e.g. bytes, bytearray, str. (Note that esp-idf distinguishes blobs and strings, this
        method always writes a blob even if a string is passed in as value.)
        Remember to call *commit*!
        """
        ...

    def commit(self) -> None:
        """
        Commits changes made by *set_xxx* methods to flash.
        """
        ...

    def get_blob(self, key: str, buffer: bytearray, /) -> int:
        """
        Reads the value of the blob for the specified key into the buffer, which must be a bytearray.
        Returns the actual length read. Raises an OSError if the key does not exist, has a different
        type, or if the buffer is too small.
        """
        ...

    def erase_key(self, key: str, /) -> None:
        """
        Erases a key-value pair.
        """
        ...

    def __init__(self, namespace: str, /) -> None:
        """
        Create an object providing access to a namespace (which is automatically created if not
        present).
        """

class Partition(AbstractBlockDev):
    """
    This class gives access to the partitions in the device's flash memory and includes
    methods to enable over-the-air (OTA) updates.
    """

    RUNNING: Final[int] = 1
    TYPE_APP: Final[int] = 0
    TYPE_DATA: Final[int] = 1
    BOOT: Final[int] = 0

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
    def ioctl(self, op: int, arg) -> None:
        """
        These methods implement the simple and :ref:`extended
        <block-device-interface>` block protocol defined by
        :class:`vfs.AbstractBlockDev`.
        """
        ...

    @overload
    def ioctl(self, op: int) -> int:
        """
        These methods implement the simple and :ref:`extended
        <block-device-interface>` block protocol defined by
        :class:`vfs.AbstractBlockDev`.
        """
        ...

    def set_boot(self) -> None:
        """
        Sets the partition as the boot partition.

        ``Note:`` Do not enter :func:`deepsleep<machine.deepsleep>` after changing
           the OTA boot partition, without first performing a hard
           :func:`reset<machine.reset>` or power cycle. This ensures the bootloader
           will validate the new image before booting.
        """
        ...

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

    def info(self) -> Tuple:
        """
        Returns a 6-tuple ``(type, subtype, addr, size, label, encrypted)``.
        """
        ...

    @staticmethod
    def find(type: int = TYPE_APP, subtype: int = 0xFF, /, label: str | None = None) -> List:
        """
        Find a partition specified by *type*, *subtype* and *label*.  Returns a
        (possibly empty) list of Partition objects. Note: ``subtype=0xff`` matches any subtype
        and ``label=None`` matches any label.

        *block_size* specifies the byte size of an individual block used by the returned
        objects.
        """
        ...

    def get_next_update(self) -> Partition:
        """
        Gets the next update partition after this one, and returns a new Partition object.
        Typical usage is ``Partition(Partition.RUNNING).get_next_update()``
        which returns the next partition to update given the current running one.
        """
        ...

    @classmethod
    def mark_app_valid_cancel_rollback(cls) -> None:
        """
        Signals that the current boot is considered successful.
        Calling ``mark_app_valid_cancel_rollback`` is required on the first boot of a new
        partition to avoid an automatic rollback at the next boot.
        This uses the ESP-IDF "app rollback" feature with "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE"
        and  an ``OSError(-261)`` is raised if called on firmware that doesn't have the
        feature enabled.
        It is OK to call ``mark_app_valid_cancel_rollback`` on every boot and it is not
        necessary when booting firmware that was loaded using esptool.
        """
        ...

    def __init__(self, id: str, block_size=4096, /) -> None:
        """
        Create an object representing a partition.

        """

class RMT:
    """
    The RMT (Remote Control) module, specific to the ESP32, was originally designed
    to send and receive infrared remote control signals. However, due to a flexible
    design and very accurate (as low as 12.5ns) pulse generation, it can also be
    used to transmit or receive many other types of digital signals::

        import esp32
        from machine import Pin

        r = esp32.RMT(0, pin=Pin(18), clock_div=8)
        r  # RMT(channel=0, pin=18, source_freq=80000000, clock_div=8, idle_level=0)

        # To apply a carrier frequency to the high output
        r = esp32.RMT(0, pin=Pin(18), clock_div=8, tx_carrier=(38000, 50, 1))

        # The channel resolution is 100ns (1/(source_freq/clock_div)).
        r.write_pulses((1, 20, 2, 40), 0)  # Send 0 for 100ns, 1 for 2000ns, 0 for 200ns, 1 for 4000ns

    The input to the RMT module is an 80MHz clock (in the future it may be able to
    configure the input clock but, for now, it's fixed). ``clock_div`` *divides*
    the clock input which determines the resolution of the RMT channel. The
    numbers specified in ``write_pulses`` are multiplied by the resolution to
    define the pulses.

    ``clock_div`` is an 8-bit divider (0-255) and each pulse can be defined by
    multiplying the resolution by a 15-bit (0-32,768) number. There are eight
    channels (0-7) and each can have a different clock divider.

    So, in the example above, the 80MHz clock is divided by 8. Thus the
    resolution is (1/(80Mhz/8)) 100ns. Since the ``start`` level is 0 and toggles
    with each number, the bitstream is ``0101`` with durations of [100ns, 2000ns,
    100ns, 4000ns].

    For more details see Espressif's `ESP-IDF RMT documentation.
    <https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/rmt.html>`_.

    .. Warning::
       The current MicroPython RMT implementation lacks some features, most notably
       receiving pulses. RMT should be considered a
       *beta feature* and the interface may change in the future.
    """

    PULSE_MAX: Final[int] = 32767
    @classmethod
    def source_freq(cls) -> int:
        """
        Returns the source clock frequency. Currently the source clock is not
        configurable so this will always return 80MHz.
        """
        ...

    def loop(self, enable_loop: bool, /) -> None:
        """
        Configure looping on the channel. *enable_loop* is bool, set to ``True`` to
        enable looping on the *next* call to `RMT.write_pulses`. If called with
        ``False`` while a looping sequence is currently being transmitted then the
        current loop iteration will be completed and then transmission will stop.
        """
        ...

    def wait_done(self, *, timeout: int = 0) -> bool:
        """
        Returns ``True`` if the channel is idle or ``False`` if a sequence of
        pulses started with `RMT.write_pulses` is being transmitted. If the
        *timeout* keyword argument is given then block for up to this many
        milliseconds for transmission to complete.
        """
        ...

    @overload
    def write_pulses(self, duration: Sequence[int] | Tuple[int, ...], data: bool = True, /) -> None:
        """
        Begin transmitting a sequence. There are three ways to specify this:

        **Mode 1:** *duration* is a list or tuple of durations. The optional *data*
        argument specifies the initial output level. The output level will toggle
        after each duration.

        **Mode 2:** *duration* is a positive integer and *data* is a list or tuple
        of output levels. *duration* specifies a fixed duration for each.

        **Mode 3:** *duration* and *data* are lists or tuples of equal length,
        specifying individual durations and the output level for each.

        Durations are in integer units of the channel resolution (as
        described above), between 1 and ``PULSE_MAX`` units. Output levels
        are any value that can be converted to a boolean, with ``True``
        representing high voltage and ``False`` representing low.

        If transmission of an earlier sequence is in progress then this method will
        block until that transmission is complete before beginning the new sequence.

        If looping has been enabled with `RMT.loop`, the sequence will be
        repeated indefinitely. Further calls to this method will block until the
        end of the current loop iteration before immediately beginning to loop the
        new sequence of pulses. Looping sequences longer than 126 pulses is not
        supported by the hardware.
        """

    @overload
    def write_pulses(self, duration: int, data: Sequence[bool] | Tuple[bool, ...], /) -> None:
        """
        Begin transmitting a sequence. There are three ways to specify this:

        **Mode 1:** *duration* is a list or tuple of durations. The optional *data*
        argument specifies the initial output level. The output level will toggle
        after each duration.

        **Mode 2:** *duration* is a positive integer and *data* is a list or tuple
        of output levels. *duration* specifies a fixed duration for each.

        **Mode 3:** *duration* and *data* are lists or tuples of equal length,
        specifying individual durations and the output level for each.

        Durations are in integer units of the channel resolution (as
        described above), between 1 and ``PULSE_MAX`` units. Output levels
        are any value that can be converted to a boolean, with ``True``
        representing high voltage and ``False`` representing low.

        If transmission of an earlier sequence is in progress then this method will
        block until that transmission is complete before beginning the new sequence.

        If looping has been enabled with `RMT.loop`, the sequence will be
        repeated indefinitely. Further calls to this method will block until the
        end of the current loop iteration before immediately beginning to loop the
        new sequence of pulses. Looping sequences longer than 126 pulses is not
        supported by the hardware.
        """

    @overload
    def write_pulses(
        self,
        duration: Sequence[int] | Tuple[int, ...],
        data: List[bool] | Tuple[bool, ...] | int,
        /,
    ) -> None:
        """
        Begin transmitting a sequence. There are three ways to specify this:

        **Mode 1:** *duration* is a list or tuple of durations. The optional *data*
        argument specifies the initial output level. The output level will toggle
        after each duration.

        **Mode 2:** *duration* is a positive integer and *data* is a list or tuple
        of output levels. *duration* specifies a fixed duration for each.

        **Mode 3:** *duration* and *data* are lists or tuples of equal length,
        specifying individual durations and the output level for each.

        Durations are in integer units of the channel resolution (as
        described above), between 1 and ``PULSE_MAX`` units. Output levels
        are any value that can be converted to a boolean, with ``True``
        representing high voltage and ``False`` representing low.

        If transmission of an earlier sequence is in progress then this method will
        block until that transmission is complete before beginning the new sequence.

        If looping has been enabled with `RMT.loop`, the sequence will be
        repeated indefinitely. Further calls to this method will block until the
        end of the current loop iteration before immediately beginning to loop the
        new sequence of pulses. Looping sequences longer than 126 pulses is not
        supported by the hardware.
        """

    @staticmethod
    def bitstream_channel(value: Optional[Any] = None) -> int:
        """
        Select which RMT channel is used by the `machine.bitstream` implementation.
        *value* can be ``None`` or a valid RMT channel number.  The default RMT
        channel is the highest numbered one.

        Passing in ``None`` disables the use of RMT and instead selects a bit-banging
        implementation for `machine.bitstream`.

        Passing in no argument will not change the channel.  This function returns
        the current channel number.
        """
        ...

    def deinit(self, *args, **kwargs) -> Incomplete: ...
    def clock_div(self) -> int:
        """
        Return the clock divider. Note that the channel resolution is
        ``1 / (source_freq / clock_div)``.
        """
        ...

    def __init__(
        self,
        channel: int,
        /,
        *,
        pin: Pin | None = None,
        clock_div: int = 8,
        idle_level: bool = False,
        tx_carrier: Tuple[int, int, bool] | None = None,
    ) -> None:
        """
        This class provides access to one of the eight RMT channels. *channel* is
        required and identifies which RMT channel (0-7) will be configured. *pin*,
        also required, configures which Pin is bound to the RMT channel. *clock_div*
        is an 8-bit clock divider that divides the source clock (80MHz) to the RMT
        channel allowing the resolution to be specified. *idle_level* specifies
        what level the output will be when no transmission is in progress and can
        be any value that converts to a boolean, with ``True`` representing high
        voltage and ``False`` representing low.

        To enable the transmission carrier feature, *tx_carrier* should be a tuple
        of three positive integers: carrier frequency, duty percent (``0`` to
        ``100``) and the output level to apply the carrier to (a boolean as per
        *idle_level*).
        """
