# -*- coding: utf-8 -*-

import asyncio
import os
from logging import getLogger
from typing import Sequence

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from dbus_next.errors import DBusError

logger = getLogger(__name__)

UDISKS2_BUS_NAME = "org.freedesktop.UDisks2"


def list_volumes_sync() -> Sequence[str]:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(list_volumes())


async def list_volumes() -> Sequence[str]:
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    introspection = None
    with open(
        os.path.join(os.path.dirname(__file__), "dbus", "org.freedesktop.UDisks2.xml"), "r"
    ) as f:
        introspection = f.read()

    object_manager_introspection = None
    with open(
        os.path.join(os.path.dirname(__file__), "dbus", "org.freedesktop.DBus.ObjectManager.xml"),
        "r",
    ) as f:
        object_manager_introspection = f.read()

    proxy_object = bus.get_proxy_object(
        UDISKS2_BUS_NAME, "/org/freedesktop/UDisks2/Manager", introspection
    )

    interface = proxy_object.get_interface("org.freedesktop.UDisks2.Manager")

    block_devices = await interface.call_get_block_devices({})
    logger.debug(f"Block devices: {block_devices}")

    proxy_object = bus.get_proxy_object(
        UDISKS2_BUS_NAME, "/org/freedesktop/UDisks2", object_manager_introspection
    )
    interface = proxy_object.get_interface("org.freedesktop.DBus.ObjectManager")
    managed_objects = await interface.call_get_managed_objects()
    logger.debug(f"Managed objects: {managed_objects}")

    # Find all drives
    drives = []
    for device, values in managed_objects.items():
        type = next(iter(values))
        if type == "org.freedesktop.UDisks2.Drive":
            drives.append(device)
    logger.debug(f"\nDrives: {drives}\n")

    discovered_usb_drives = []
    for a_drive in drives:
        proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME, a_drive, introspection)
        interface = proxy_object.get_interface("org.freedesktop.UDisks2.Drive")
        connection_bus = await interface.get_connection_bus()
        time_media_detected = await interface.get_time_media_detected()
        if connection_bus == "usb":
            discovered_usb_drives.append(
                {
                    "drive": a_drive,
                    "time_media_detected": time_media_detected,
                }
            )
    logger.debug(f"\nUSB Drives: {discovered_usb_drives}\n")

    if len(discovered_usb_drives) == 0:
        logger.debug("No USB drive found")
        return []

    # Find the block devices associated with each USB drive
    discovered_block_devices = []
    for block_device in block_devices:
        proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME, block_device, introspection)
        interface = proxy_object.get_interface("org.freedesktop.UDisks2.Block")
        id_usage = await interface.get_id_usage()
        if id_usage != "filesystem":
            continue
        a_drive = await interface.get_drive()
        for dictionary in discovered_usb_drives:
            if dictionary["drive"] == a_drive:
                discovered_block_devices.append(
                    {
                        "block_device": block_device,
                        "time_media_detected": dictionary["time_media_detected"],
                    }
                )
                break
    logger.debug(f"\nDiscovered Block Devices: {discovered_block_devices}\n")

    if len(discovered_block_devices) == 0:
        logger.debug("No block devices found")
        return []

    # In case there are multiple block devices detected, sort by time the device was detected.
    # Most recently detected are placed first.
    discovered_block_devices = sorted(
        discovered_block_devices, key=lambda x: x.get("time_media_detected")
    )
    discovered_block_devices = [i["block_device"] for i in discovered_block_devices]

    discovered_mount_points = []
    for block_device in discovered_block_devices:
        # Make sure that the filesystem is mounted and get the mount point.
        proxy_object = bus.get_proxy_object(UDISKS2_BUS_NAME, block_device, introspection)
        interface = proxy_object.get_interface("org.freedesktop.UDisks2.Filesystem")

        mount_point = None
        try:
            mount_point = await interface.call_mount({})
        except DBusError as error:
            if "is already mounted" not in error.text:
                raise
            mount_points = await interface.get_mount_points()
            # todo Double check that I don't need to account for endianess or other encoding formats here.
            mount_point = mount_points[0].decode("utf-8")
        discovered_mount_points.append(mount_point.rstrip("\x00"))
    logger.debug(f"\nFilesystem Mount Points: {discovered_mount_points}\n")

    return discovered_mount_points
