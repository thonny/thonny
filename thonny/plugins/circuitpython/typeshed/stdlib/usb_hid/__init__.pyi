"""USB Human Interface Device

The `usb_hid` module allows you to output data as a HID device."""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

from circuitpython_typing import ReadableBuffer

devices: Tuple[Device, ...]
"""Tuple of all active HID device interfaces.
The default set of devices is ``Device.KEYBOARD, Device.MOUSE, Device.CONSUMER_CONTROL``,
On boards where `usb_hid` is disabled by default, `devices` is an empty tuple.

If a boot device is enabled by `usb_hid.enable()`, *and* the host has requested a boot device,
the `devices` tuple is **replaced** when ``code.py`` starts with a single-element tuple
containing a `Device` that describes the boot device chosen (keyboard or mouse).
The request for a boot device overrides any other HID devices.
"""

def disable() -> None:
    """Do not present any USB HID devices to the host computer.
    Can be called in ``boot.py``, before USB is connected.
    The HID composite device is normally enabled by default,
    but on some boards with limited endpoints, including STM32F4,
    it is disabled by default. You must turn off another USB device such
    as `usb_cdc` or `storage` to free up endpoints for use by `usb_hid`.
    """

def enable(devices: Optional[Sequence[Device]], boot_device: int = 0) -> None:
    """Specify which USB HID devices that will be available.
    Can be called in ``boot.py``, before USB is connected.

    :param Sequence devices: `Device` objects.
      If `devices` is empty, HID is disabled. The order of the ``Devices``
      may matter to the host. For instance, for MacOS, put the mouse device
      before any Gamepad or Digitizer HID device or else it will not work.
    :param int boot_device: If non-zero, inform the host that support for a
      a boot HID device is available.
      If ``boot_device=1``, a boot keyboard is available.
      If ``boot_device=2``, a boot mouse is available. No other values are allowed.
      See below.

    If you enable too many devices at once, you will run out of USB endpoints.
    The number of available endpoints varies by microcontroller.
    CircuitPython will go into safe mode after running ``boot.py`` to inform you if
    not enough endpoints are available.

    **Boot Devices**

    Boot devices implement a fixed, predefined report descriptor, defined in
    https://www.usb.org/sites/default/files/hid1_12.pdf, Appendix B. A USB host
    can request to use the boot device if the USB device says it is available.
    Usually only a BIOS or other kind of limited-functionality
    host needs boot keyboard support.

    For example, to make a boot keyboard available, you can use this code::

      usb_hid.enable((Device.KEYBOARD), boot_device=1)  # 1 for a keyboard

    If the host requests the boot keyboard, the report descriptor provided by `Device.KEYBOARD`
    will be ignored, and the predefined report descriptor will be used.
    But if the host does not request the boot keyboard,
    the descriptor provided by `Device.KEYBOARD` will be used.

    The HID boot device must usually be the first or only device presented by CircuitPython.
    The HID device will be USB interface number 0.
    To make sure it is the first device, disable other USB devices, including CDC and MSC (CIRCUITPY).
    If you specify a non-zero ``boot_device``, and it is not the first device, CircuitPython
    will enter safe mode to report this error.
    """
    ...

def get_boot_device() -> int:
    """
    :return: the boot device requested by the host, if any.
      Returns 0 if the host did not request a boot device, or if `usb_hid.enable()`
      was called with ``boot_device=0``, the default, which disables boot device support.
      If the host did request a boot device,
      returns the value of ``boot_device`` set in `usb_hid.enable()`:
      ``1`` for a boot keyboard, or ``2`` for boot mouse.
      However, the standard devices provided by CircuitPython, `Device.KEYBOARD` and `Device.MOUSE`,
      describe reports that match the boot device reports, so you don't need to check this
      if you are using those devices.
    :rtype int:
    """

def set_interface_name(interface_name: str) -> None:
    """Override HID interface name in the USB Interface Descriptor.

    ``interface_name`` must be an ASCII string (or buffer) of at most 126.

    This method must be called in boot.py to have any effect.

    Not available on boards without native USB support.
    """
    ...

class Device:
    """HID Device specification"""

    def __init__(
        self,
        *,
        report_descriptor: ReadableBuffer,
        usage_page: int,
        usage: int,
        report_ids: Sequence[int],
        in_report_lengths: Sequence[int],
        out_report_lengths: Sequence[int],
    ) -> None:
        """Create a description of a USB HID device. The actual device is created when you
        pass a `Device` to `usb_hid.enable()`.

        :param ReadableBuffer report_descriptor: The USB HID Report descriptor bytes. The descriptor is not
          not verified for correctness; it is up to you to make sure it is not malformed.
        :param int usage_page: The Usage Page value from the descriptor. Must match what is in the descriptor.
        :param int usage: The Usage value from the descriptor. Must match what is in the descriptor.
        :param Sequence[int] report_ids: Sequence of report ids used by the descriptor.
          If the ``report_descriptor`` does not specify any report IDs, use ``(0,)``.
        :param Sequence[int] in_report_lengths: Sequence of sizes in bytes of the HID reports sent to the host.
          The sizes are in order of the ``report_ids``.
          Use a size of ``0`` for a report that is not an IN report.
          "IN" is with respect to the host.
        :param int out_report_lengths: Sequence of sizes in bytes of the HID reports received from the host.
          The sizes are in order of the ``report_ids``.
          Use a size of ``0`` for a report that is not an OUT report.
          "OUT" is with respect to the host.

        ``report_ids``, ``in_report_lengths``, and ``out_report_lengths`` must all have the
        same number of elements.

        Here is an example of a `Device` with a descriptor that specifies two report IDs, 3 and 4.
        Report ID 3 sends an IN report of length 5, and receives an OUT report of length 6.
        Report ID 4 sends an IN report of length 2, and does not receive an OUT report::

            device = usb_hid.Device(
                descriptor=b"...",         # Omitted for brevity.
                report_ids=(3, 4),
                in_report_lengths=(5, 2),
                out_report_lengths=(6, 0),
            )

        The HID device is able to wake up a suspended (sleeping) host computer.
        See `send_report()` for details.
        """
        ...
    KEYBOARD: Device
    """Standard keyboard device supporting keycodes 0x00-0xDD, modifiers 0xE-0xE7, and five LED indicators.
    Uses Report ID 1 for its IN and OUT reports.
    """

    MOUSE: Device
    """Standard mouse device supporting five mouse buttons, X and Y relative movements from -127 to 127
    in each report, and a relative mouse wheel change from -127 to 127 in each report.
    Uses Report ID 2 for its IN report.
    """

    CONSUMER_CONTROL: Device
    """Consumer Control device supporting sent values from 1-652, with no rollover.
    Uses Report ID 3 for its IN report."""
    def send_report(
        self, report: ReadableBuffer, report_id: Optional[int] = None
    ) -> None:
        """Send an HID report. If the device descriptor specifies zero or one report id's,
        you can supply `None` (the default) as the value of ``report_id``.
        Otherwise you must specify which report id to use when sending the report.

        If the USB host is suspended (sleeping), then `send_report()` will request that the host wake up.
        The ``report`` itself will be discarded, to prevent unwanted extraneous characters,
        mouse clicks, etc.

        Note: Host operating systems allow enabling and disabling specific devices
        and kinds of devices to do wakeup.
        The defaults are different for different operating systems.
        For instance, on Linux, only the primary keyboard may be enabled.
        In addition, there may be USB wakeup settings in the host computer BIOS/UEFI.
        """
        ...

    def get_last_received_report(
        self, report_id: Optional[int] = None
    ) -> Optional[bytes]:
        """Get the last received HID OUT or feature report for the given report ID.
        The report ID may be omitted if there is no report ID, or only one report ID.
        Return `None` if nothing received. After returning a report, subsequent calls
        will return `None` until next report is received.
        """
        ...
    usage_page: int
    """The device usage page identifier, which designates a category of device. (read-only)"""
    usage: int
    """The device usage identifier, which designates a specific kind of device. (read-only)

    For example, Keyboard is 0x06 within the generic desktop usage page 0x01.
    Mouse is 0x02 within the same usage page."""
