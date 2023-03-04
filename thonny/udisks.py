# -*- coding: utf-8 -*-

import asyncio
from typing import Sequence
from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from dbus_next.errors import DBusError

UDISKS2_BUS_NAME = 'org.freedesktop.UDisks2'

loop = asyncio.get_event_loop()


# todo Add actual error-checking and log diagnostic information appropriately.
async def list_volumes_udisks() -> Sequence[str]:
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # with open('introspection.xml', 'r') as f:
    #     introspection = f.read()

    # todo Apparently, the introspections should be stored as strings instead of fetched dynamically as done here.
    introspection = await bus.introspect(UDISKS2_BUS_NAME, '/org/freedesktop/UDisks2/Manager')

    proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME,
                                        '/org/freedesktop/UDisks2/Manager',
                                        introspection)

    interface = proxy_object.get_interface('org.freedesktop.UDisks2.Manager')

    block_devices = await interface.call_get_block_devices({})
    print(f"Block devices: {block_devices}")

    introspection = await bus.introspect(UDISKS2_BUS_NAME, '/org/freedesktop/UDisks2')
    proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME,
                                        '/org/freedesktop/UDisks2',
                                        introspection)
    interface = proxy_object.get_interface('org.freedesktop.DBus.ObjectManager')
    managed_objects = await interface.call_get_managed_objects()
    print(f"Managed objects: {managed_objects}")

    # Find all drives
    drives = []
    for device, values in managed_objects.items():
        type = next(iter(values))
        if type == "org.freedesktop.UDisks2.Drive":
            drives.append(device)
    print(f"\nDrives: {drives}\n")

    # Filter down to RP2040 USB drives only
    rp2040_usb_drives = []
    for drive in drives:
        drive_introspection = await bus.introspect(UDISKS2_BUS_NAME, drive)
        proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME,
                                            drive,
                                            drive_introspection)
        interface = proxy_object.get_interface("org.freedesktop.UDisks2.Drive")
        connection_bus = await interface.get_connection_bus()
        vendor = await interface.get_vendor()
        model = await interface.get_model()
        if connection_bus == "usb" and vendor == "RPI" and model == "RP2":
            rp2040_usb_drives.append(drive)
    print(f"\nRP2040 USB Drives: {rp2040_usb_drives}\n")

    if len(rp2040_usb_drives) == 0:
        print("No RP2040 USB drive found")
        return []

    if len(rp2040_usb_drives) > 1:
        print("Multiple RP2040 USB drives found")

    # Find the block devices associated with the RP2040 USB drive
    rp2040_block_devices = []
    for block_device in block_devices:
        block_device_introspection = await bus.introspect(UDISKS2_BUS_NAME, block_device)
        proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME,
                                            block_device,
                                            block_device_introspection)
        interface = proxy_object.get_interface("org.freedesktop.UDisks2.Block")
        id_label = await interface.get_id_label()
        drive = await interface.get_drive()
        if id_label == "RPI-RP2" and drive in rp2040_usb_drives:
            rp2040_block_devices.append(block_device)
    print(f"\nRP2040 Block Devices: {rp2040_block_devices}\n")

    if len(rp2040_block_devices) == 0:
        print("No RP2040 block devices found")
        return []

    # Assume that we only want the first RP2040 block device for now.
    rp2040_block_device = rp2040_block_devices[0]

    # Make sure that the RP2040 filesystem is mounted and get the mount point.
    block_device_introspection = await bus.introspect(UDISKS2_BUS_NAME, rp2040_block_device)
    proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME,
                                        rp2040_block_device,
                                        block_device_introspection)
    interface = proxy_object.get_interface("org.freedesktop.UDisks2.Filesystem")

    mount_point = None
    try:
        mount_point = await interface.call_mount({})
    except DBusError as error:
        if "is already mounted" not in error.text:
            raise
        mount_points = await interface.get_mount_points()
        print(f"\nRP2040 Filesystem Mount Points: {mount_points}\n")
        # todo Double check that I don't need to account for endianess or other encoding formats here.
        mount_point = mount_points[0].decode("utf-8")
    print(f"\nRP2040 Filesystem Mount Point: {mount_point}\n")

    await loop.create_future()
    return mount_point


loop.run_until_complete(list_volumes_udisks())
