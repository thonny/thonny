"""
functionality specific to the ESP32.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/esp32.rst.
====================================================

.. module:: esp32
    :synopsis: functionality specific to the ESP32

The ``esp32`` module contains functions and classes specifically aimed at
controlling ESP32 modules.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final, List, Tuple, overload, ClassVar

from machine import Pin
from uio import AnyReadableBuf
from uos import AbstractBlockDev

def wake_on_touch(wake: bool, /) -> None:
    """
    Configure whether or not a touch will wake the device from sleep.
    *wake* should be a boolean value.
   """

def wake_on_ext0(pin: Pin | None, level: int, /) -> None:
    """
    Configure how EXT0 wakes the device from sleep.  *pin* can be ``None``
    or a valid Pin object.  *level* should be ``esp32.WAKEUP_ALL_LOW`` or
    ``esp32.WAKEUP_ANY_HIGH``.
   """

def wake_on_ext1(pins: List[Pin] | Tuple[Pin, ...] | None, level: int, /) -> None:
    """
    Configure how EXT1 wakes the device from sleep.  *pins* can be ``None``
    or a tuple/list of valid Pin objects.  *level* should be ``esp32.WAKEUP_ALL_LOW``
    or ``esp32.WAKEUP_ANY_HIGH``.
   """

def raw_temperature() -> int:
    """
    Read the raw value of the internal temperature sensor, returning an integer.
   """

def hall_sensor() -> int:
    """
    Read the raw value of the internal Hall sensor, returning an integer.
   """

def idf_heap_info(capabilities: int) -> List[Tuple[int, int, int, int]]:
    """
    Returns information about the ESP-IDF heap memory regions. One of them contains
    the MicroPython heap and the others are used by ESP-IDF, e.g., for network
    buffers and other data. This data is useful to get a sense of how much memory
    is available to ESP-IDF and the networking stack in particular. It may shed
    some light on situations where ESP-IDF operations fail due to allocation failures.
    The information returned is *not* useful to troubleshoot Python allocation failures,
    use `micropython.mem_info()` instead.
    
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
   """

HEAP_DATA: Final[int] = ...
"""
Used in `idf_heap_info`.
"""

HEAP_EXEC: Final[int] = ...
"""
Used in `idf_heap_info`.
"""

WAKEUP_ALL_LOW: Final[int] = ...
"""
Selects the wake level for pins.
"""

WAKEUP_ANY_HIGH: Final[int] = ...
"""
Selects the wake level for pins.
"""

class Partition(AbstractBlockDev):
    """
   This class gives access to the partitions in the device's flash memory and includes
   methods to enable over-the-air (OTA) updates.
   """

    BOOT: ClassVar[int] = ...
    """
Used in the `Partition` constructor to fetch various partitions: ``BOOT`` is the
    partition that will be booted at the next reset and ``RUNNING`` is the currently
    running partition.
   """

    RUNNING: ClassVar[int] = ...
    """
Used in the `Partition` constructor to fetch various partitions: ``BOOT`` is the
    partition that will be booted at the next reset and ``RUNNING`` is the currently
    running partition.
   """

    TYPE_APP: ClassVar[int] = ...
    """
Used in `Partition.find` to specify the partition type: ``APP`` is for bootable
    firmware partitions (typically labelled ``factory``, ``ota_0``, ``ota_1``), and
    ``DATA`` is for other partitions, e.g. ``nvs``, ``otadata``, ``phy_init``, ``vfs``.
   """

    TYPE_DATA: ClassVar[int] = ...
    """
Used in `Partition.find` to specify the partition type: ``APP`` is for bootable
    firmware partitions (typically labelled ``factory``, ``ota_0``, ``ota_1``), and
    ``DATA`` is for other partitions, e.g. ``nvs``, ``otadata``, ``phy_init``, ``vfs``.
   """
    def __init__(self, id: str | int, /):
        """
       Create an object representing a partition.  *id* can be a string which is the label
       of the partition to retrieve, or one of the constants: ``BOOT`` or ``RUNNING``.
      """
    @staticmethod
    def find(
        type: int = TYPE_APP, subtype: int = 0xFF, label: str | None = None, /
    ) -> List["Partition"]:
        """
       Find a partition specified by *type*, *subtype* and *label*.  Returns a
       (possibly empty) list of Partition objects. Note: ``subtype=0xff`` matches any subtype
       and ``label=None`` matches any label.
      """
    def info(self) -> (int, int, int, int, str, bool):
        """
       Returns a 6-tuple ``(type, subtype, addr, size, label, encrypted)``.
      """
    def set_boot(self) -> None:
        """
       Sets the partition as the boot partition.
      """
    def get_next_update(self) -> "Partition":
        """
       Gets the next update partition after this one, and returns a new Partition object.
       Typical usage is ``Partition(Partition.RUNNING).get_next_update()``
       which returns the next partition to update given the current running one.
      """
    @staticmethod
    def mark_app_valid_cancel_rollback() -> None:
        """
       Signals that the current boot is considered successful.
       Calling ``mark_app_valid_cancel_rollback`` is required on the first boot of a new
       partition to avoid an automatic rollback at the next boot.
       This uses the ESP-IDF "app rollback" feature with "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE"
       and  an ``OSError(-261)`` is raised if called on firmware that doesn't have the
       feature enabled.
       It is OK to call ``mark_app_valid_cancel_rollback`` on every boot and it is not
       necessary when booting firmare that was loaded using esptool.
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

    def __init__(
        self,
        channel: int,
        /,
        *,
        pin: Pin | None = None,
        clock_div: int = 8,
        idle_level: bool = False,
        tx_carrier: Tuple[int, int, bool] | None = None,
    ):
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
    def source_freq(self) -> int:
        """
       Returns the source clock frequency. Currently the source clock is not
       configurable so this will always return 80MHz.
      """
    def clock_div(self) -> int:
        """
       Return the clock divider. Note that the channel resolution is
       ``1 / (source_freq / clock_div)``.
      """
    def wait_done(self, *, timeout: int = 0) -> bool:
        """
       Returns ``True`` if the channel is idle or ``False`` if a sequence of
       pulses started with `RMT.write_pulses` is being transmitted. If the
       *timeout* keyword argument is given then block for up to this many
       milliseconds for transmission to complete.
      """
    def loop(self, enable_loop: bool, /) -> None:
        """
       Configure looping on the channel. *enable_loop* is bool, set to ``True`` to
       enable looping on the *next* call to `RMT.write_pulses`. If called with
       ``False`` while a looping sequence is currently being transmitted then the
       current loop iteration will be completed and then transmission will stop.
      """
    @overload
    def write_pulses(
        self, duration: List[int] | Tuple[int, ...], data: bool = True, /
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
       
       Durations are in integer units of the channel resolution (as described
       above), between 1 and 32767 units. Output levels are any value that can
       be converted to a boolean, with ``True`` representing high voltage and
       ``False`` representing low.
       
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
        self, duration: int, data: List[bool] | Tuple[bool, ...], /
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
       
       Durations are in integer units of the channel resolution (as described
       above), between 1 and 32767 units. Output levels are any value that can
       be converted to a boolean, with ``True`` representing high voltage and
       ``False`` representing low.
       
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
        duration: List[int] | Tuple[int, ...],
        data: List[bool] | Tuple[bool, ...],
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
       
       Durations are in integer units of the channel resolution (as described
       above), between 1 and 32767 units. Output levels are any value that can
       be converted to a boolean, with ``True`` representing high voltage and
       ``False`` representing low.
       
       If transmission of an earlier sequence is in progress then this method will
       block until that transmission is complete before beginning the new sequence.
       
       If looping has been enabled with `RMT.loop`, the sequence will be
       repeated indefinitely. Further calls to this method will block until the
       end of the current loop iteration before immediately beginning to loop the
       new sequence of pulses. Looping sequences longer than 126 pulses is not
       supported by the hardware.
      """

class ULP:
    """
   This class provides access to the Ultra-Low-Power co-processor.
   """

    def __init__(self):
        """
       This class provides access to the Ultra-Low-Power co-processor.
      """
    def set_wakeup_period(self, period_index: int, period_us: int, /) -> None:
        """
       Set the wake-up period.
      """
    def load_binary(self, load_addr: int, program_binary: AnyReadableBuf, /) -> None:
        """
       Load a *program_binary* into the ULP at the given *load_addr*.
      """
    def run(self, entry_point: int, /) -> None:
        """
       Start the ULP running at the given *entry_point*.
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

    def __init__(self, namespace: str, /):
        """
       Create an object providing access to a namespace (which is automatically created if not
       present).
      """
    def set_i32(self, key: str, value: int, /) -> None:
        """
       Sets a 32-bit signed integer value for the specified key. Remember to call *commit*!
      """
    def get_i32(self, key: str, /) -> int:
        """
       Returns the signed integer value for the specified key. Raises an OSError if the key does not
       exist or has a different type.
      """
    def set_blob(self, key: str, value: AnyReadableBuf, /) -> None:
        """
       Sets a binary blob value for the specified key. The value passed in must support the buffer
       protocol, e.g. bytes, bytearray, str. (Note that esp-idf distinguishes blobs and strings, this
       method always writes a blob even if a string is passed in as value.)
       Remember to call *commit*!
      """
    def get_blob(self, key: str, buffer: bytearray, /) -> int:
        """
       Reads the value of the blob for the specified key into the buffer, which must be a bytearray.
       Returns the actual length read. Raises an OSError if the key does not exist, has a different
       type, or if the buffer is too small.
      """
    def erase_key(self, key: str, /) -> None:
        """
       Erases a key-value pair.
      """
    def commit(self) -> None:
        """
       Commits changes made by *set_xxx* methods to flash.
      """
