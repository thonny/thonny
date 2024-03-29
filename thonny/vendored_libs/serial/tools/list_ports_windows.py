#! python
#
# Enumerate serial ports on Windows including a human-readable description
# and hardware information.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
#
# SPDX-License-Identifier:    BSD-3-Clause

# List all the com port devices in windows.
# Feature:
# 1. Using CfgMgr32 only;
# 2. Query usb information via DeviceIoControl;
# 3. Object-oriented code.

from __future__ import absolute_import

import ctypes
import re
from serial.tools.list_ports_common import ListPortInfo


class GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', ctypes.c_uint32),
        ('Data2', ctypes.c_uint16),
        ('Data3', ctypes.c_uint16),
        ('Data4', ctypes.c_uint8 * 8),
    ]

    def __str__(self):
        return "{{{:08x}-{:04x}-{:04x}-{}-{}}}".format(
            self.Data1,
            self.Data2,
            self.Data3,
            ''.join(["{:02x}".format(d) for d in self.Data4[:2]]),
            ''.join(["{:02x}".format(d) for d in self.Data4[2:]]),
        )

    def __eq__(self, other):
        return self.Data1 == other.Data1 \
            and self.Data2 == other.Data2 \
            and self.Data3 == other.Data3 \
            and all((self.Data4[i] == other.Data4[i] for i in range(8)))


class DEVPROPKEY(ctypes.Structure):
    _fields_ = [
        ('fmtid', GUID),
        ('pid', ctypes.c_uint32)
    ]


class USB_DEVICE_DESCRIPTOR(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bLength', ctypes.c_uint8),
        ('bDescriptorType', ctypes.c_uint8),
        ('bcdUSB', ctypes.c_uint16),
        ('bDeviceClass', ctypes.c_uint8),
        ('bDeviceSubClass', ctypes.c_uint8),
        ('bDeviceProtocol', ctypes.c_uint8),
        ('bMaxPacketSize0', ctypes.c_uint8),
        ('idVendor', ctypes.c_uint16),
        ('idProduct', ctypes.c_uint16),
        ('bcdDevice', ctypes.c_uint16),
        ('iManufacturer', ctypes.c_uint8),
        ('iProduct', ctypes.c_uint8),
        ('iSerialNumber', ctypes.c_uint8),
        ('bNumConfigurations', ctypes.c_uint8),
    ]


class USB_STRING_DESCRIPTOR(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bLength', ctypes.c_uint8),
        ('bDescriptorType', ctypes.c_uint8),
        ('bString', ctypes.c_wchar * 255),
    ]


class USB_COMMON_DESCRIPTOR(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bLength', ctypes.c_uint8),
        ('bDescriptorType', ctypes.c_uint8),
    ]


class USB_CONFIGURATION_DESCRIPTOR(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bLength', ctypes.c_uint8),
        ('bDescriptorType', ctypes.c_uint8),
        ('wTotalLength', ctypes.c_uint16),
        ('bNumInterfaces', ctypes.c_uint8),
        ('bConfigurationValue', ctypes.c_uint8),
        ('iConfiguration', ctypes.c_uint8),
        ('bmAttributes', ctypes.c_uint8),
        ('MaxPower', ctypes.c_uint8),
    ]


class USB_INTERFACE_DESCRIPTOR(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bLength', ctypes.c_uint8),
        ('bDescriptorType', ctypes.c_uint8),
        ('bInterfaceNumber', ctypes.c_uint8),
        ('bAlternateSetting', ctypes.c_uint8),
        ('bNumEndpoints', ctypes.c_uint8),
        ('bInterfaceClass', ctypes.c_uint8),
        ('bInterfaceSubClass', ctypes.c_uint8),
        ('bInterfaceProtocol', ctypes.c_uint8),
        ('iInterface', ctypes.c_uint8),
    ]


class USB_INTERFACE_ASSOCIATION_DESCRIPTOR(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bLength', ctypes.c_uint8),
        ('bDescriptorType', ctypes.c_uint8),
        ('bFirstInterface', ctypes.c_uint8),
        ('bInterfaceCount', ctypes.c_uint8),
        ('bFunctionClass', ctypes.c_uint8),
        ('bFunctionSubClass', ctypes.c_uint8),
        ('bFunctionProtocol', ctypes.c_uint8),
        ('iFunction', ctypes.c_uint8)
    ]


class USB_NODE_CONNECTION_INFORMATION_EX(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('ConnectionIndex', ctypes.c_uint32),
        ('DeviceDescriptor', USB_DEVICE_DESCRIPTOR),
        ('CurrentConfigurationValue', ctypes.c_uint8),
        ('Speed', ctypes.c_uint8),
        ('DeviceIsHub', ctypes.c_uint8),
        ('DeviceAddress', ctypes.c_uint16),
        ('NumberOfOpenPipes', ctypes.c_uint32),
        ('ConnectionStatus', ctypes.c_uint),
    ]


class SetupPacket(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bmRequest', ctypes.c_uint8),
        ('bRequest', ctypes.c_uint8),
        ('wValue', ctypes.c_uint16),
        ('wIndex', ctypes.c_uint16),
        ('wLength', ctypes.c_uint16),
    ]


class USB_DESCRIPTOR_REQUEST(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('ConnectionIndex', ctypes.c_uint32),
        ('SetupPacket', SetupPacket),
    ]


class CM_POWER_DATA(ctypes.Structure):
    _fields_ = [
        ('PD_Size', ctypes.c_uint32),
        ('PD_MostRecentPowerState', ctypes.c_int),
        ('PD_Capabilities', ctypes.c_uint32),
        ('PD_D1Latency', ctypes.c_uint32),
        ('PD_D2Latency', ctypes.c_uint32),
        ('PD_D3Latency', ctypes.c_uint32),
        ('PD_PowerStateMapping', ctypes.c_int * 7),
        ('PD_DeepestSystemWake', ctypes.c_int),
    ]


CreateFileW = ctypes.windll.kernel32.CreateFileW
CreateFileW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_void_p
]
CreateFileW.restype = ctypes.c_void_p

GetUserDefaultLangID = ctypes.windll.kernel32.GetUserDefaultLangID
GetUserDefaultLangID.restype = ctypes.c_uint16

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = [
    ctypes.c_void_p
]
CloseHandle.restype = ctypes.c_int

DeviceIoControl = ctypes.windll.kernel32.DeviceIoControl
DeviceIoControl.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_void_p
]
DeviceIoControl.restype = ctypes.c_int

RegQueryValueExW = ctypes.windll.advapi32.RegQueryValueExW
RegQueryValueExW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_wchar_p,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint32)
]
RegQueryValueExW.restype = ctypes.c_int32

RegCloseKey = ctypes.windll.advapi32.RegCloseKey
RegCloseKey.argtypes = [
    ctypes.c_void_p
]
RegCloseKey.restype = ctypes.c_int32

CM_Get_Device_Interface_List_SizeW = ctypes.windll.cfgmgr32.CM_Get_Device_Interface_List_SizeW
CM_Get_Device_Interface_List_SizeW.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(GUID),
    ctypes.c_wchar_p,
    ctypes.c_uint32
]
CM_Get_Device_Interface_List_SizeW.restype = ctypes.c_uint32

CM_Get_Device_Interface_ListW = ctypes.windll.cfgmgr32.CM_Get_Device_Interface_ListW
CM_Get_Device_Interface_ListW.argtypes = [
    ctypes.POINTER(GUID),
    ctypes.c_wchar_p,
    ctypes.c_wchar_p,
    ctypes.c_uint32,
    ctypes.c_uint32
]
CM_Get_Device_Interface_ListW.restype = ctypes.c_uint32

CM_Locate_DevNodeW = ctypes.windll.cfgmgr32.CM_Locate_DevNodeW
CM_Locate_DevNodeW.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_wchar_p,
    ctypes.c_uint32
]
CM_Locate_DevNodeW.restype = ctypes.c_uint32

CM_Get_DevNode_PropertyW = ctypes.windll.cfgmgr32.CM_Get_DevNode_PropertyW
CM_Get_DevNode_PropertyW.argtypes = [
    ctypes.c_uint32,
    ctypes.POINTER(DEVPROPKEY),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32
]
CM_Get_DevNode_PropertyW.restype = ctypes.c_uint32

CM_MapCrToWin32Err = ctypes.windll.cfgmgr32.CM_MapCrToWin32Err
CM_MapCrToWin32Err.argtypes = [
    ctypes.c_uint32,
    ctypes.c_uint32
]
CM_MapCrToWin32Err.restype = ctypes.c_uint32

CM_Get_Device_Interface_PropertyW = ctypes.windll.cfgmgr32.CM_Get_Device_Interface_PropertyW
CM_Get_Device_Interface_PropertyW.argtypes = [
    ctypes.c_wchar_p,
    ctypes.POINTER(DEVPROPKEY),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32
]
CM_Get_Device_Interface_PropertyW.restype = ctypes.c_uint32

CM_Get_DevNode_Status = ctypes.windll.cfgmgr32.CM_Get_DevNode_Status
CM_Get_DevNode_Status.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32,
    ctypes.c_uint32
]
CM_Get_DevNode_Status.restype = ctypes.c_uint32

CM_Get_Parent = ctypes.windll.cfgmgr32.CM_Get_Parent
CM_Get_Parent.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32,
    ctypes.c_uint32
]
CM_Get_Parent.restype = ctypes.c_uint32

CM_Open_DevNode_Key = ctypes.windll.cfgmgr32.CM_Open_DevNode_Key
CM_Open_DevNode_Key.argtypes = [
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_void_p,
    ctypes.c_uint32
]
CM_Open_DevNode_Key.restype = ctypes.c_uint32

GUID_DEVINTERFACE_USB_HUB = GUID(0xf18a0e88, 0xc30c, 0x11d0, (0x88, 0x15, 0x00, 0xa0, 0xc9, 0x06, 0xbe, 0xd8))
GUID_DEVINTERFACE_COMPORT = GUID(0X86E0D1E0, 0X8089, 0X11D0, (0X9C, 0XE4, 0X08, 0X00, 0X3E, 0X30, 0X1F, 0X73))
GUID_DEVINTERFACE_MODEM = GUID(0x2c7089aa, 0x2e0e, 0x11d1, (0xb1, 0x14, 0x00, 0xc0, 0x4f, 0xc2, 0xaa, 0xe4))
GUID_DEVINTERFACE_USB_HOST_CONTROLLER = GUID(0x3abf6f2d, 0x71c4, 0x462a, (0x8a, 0x92, 0x1e, 0x68, 0x61, 0xe6, 0xaf, 0x27))

CM_GET_DEVICE_INTERFACE_LIST_PRESENT = 0
CM_LOCATE_DEVNODE_NORMAL = 0
CR_SUCCESS = 0
CR_BUFFER_SMALL = 26
ERROR_MORE_DATA = 234
ERROR_SUCCESS = 0

DEVPKEY_NAME = DEVPROPKEY((0xb725f130, 0x47ef, 0x101a, (0xa5, 0xf1, 0x02, 0x60, 0x8c, 0x9e, 0xeb, 0xac)), 10)
DEVPKEY_Device_DeviceDesc = DEVPROPKEY((0xa45c254e, 0xdf1c, 0x4efd, (0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0)), 2)
DEVPKEY_Device_Manufacturer = DEVPROPKEY((0xa45c254e, 0xdf1c, 0x4efd, (0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0)), 13)
DEVPKEY_Device_FriendlyName = DEVPROPKEY((0xa45c254e, 0xdf1c, 0x4efd, (0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0)), 14)
DEVPKEY_Device_PowerData = DEVPROPKEY((0xa45c254e, 0xdf1c, 0x4efd, (0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0)), 32)
DEVPKEY_Device_LocationPaths = DEVPROPKEY((0xa45c254e, 0xdf1c, 0x4efd, (0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0)), 37)
DEVPKEY_Device_Address = DEVPROPKEY((0xa45c254e, 0xdf1c, 0x4efd, (0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0)), 30)
DEVPKEY_Device_InstanceId = DEVPROPKEY((0x78c34fc8, 0x104a, 0x4aca, (0x9e, 0xa4, 0x52, 0x4d, 0x52, 0x99, 0x6e, 0x57)), 256)
DEVPKEY_Device_BusReportedDeviceDesc = DEVPROPKEY((0x540b947e, 0x8b40, 0x45bc, (0xa8, 0xa2, 0x6a, 0x0b, 0x89, 0x4c, 0xbd, 0xa2)), 4)

DEVPROP_TYPEMOD_ARRAY = 0x00001000
DEVPROP_TYPEMOD_LIST = 0x00002000
DEVPROP_TYPE_UINT32 = 0x00000007
DEVPROP_TYPE_STRING = 0x00000012
DEVPROP_TYPE_BYTE = 0x00000003
DEVPROP_TYPE_BINARY = (DEVPROP_TYPE_BYTE | DEVPROP_TYPEMOD_ARRAY)
DEVPROP_TYPE_STRING_LIST = (DEVPROP_TYPE_STRING | DEVPROP_TYPEMOD_LIST)

KEY_READ = 0x20019
RegDisposition_OpenExisting = 1
CM_REGISTRY_HARDWARE = 0

USB_REQUEST_GET_DESCRIPTOR = 6
USB_DEVICE_DESCRIPTOR_TYPE = 1
USB_CONFIGURATION_DESCRIPTOR_TYPE = 2
USB_STRING_DESCRIPTOR_TYPE = 3
USB_INTERFACE_DESCRIPTOR_TYPE = 4
USB_INTERFACE_ASSOCIATION_DESCRIPTOR_TYPE = 0x0B
IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION = 2229264
IOCTL_USB_GET_NODE_CONNECTION_INFORMATION_EX = 2229320
IOCTL_USB_GET_ROOT_HUB_NAME = 2229256
IOCTL_USB_GET_NODE_CONNECTION_NAME = 2229268

GENERIC_READ = 2147483648
GENERIC_WRITE = 1073741824
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 128
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


def find_from_iterable(iterable, value):
    return next((x for x in iterable if x == value), None)


def parse_device_property(buffer, buffer_size, property_type):
    if property_type.value == DEVPROP_TYPE_STRING:
        return ctypes.wstring_at(buffer, buffer_size.value // 2 - 1)
    if property_type.value == DEVPROP_TYPE_UINT32:
        return ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint32)).contents.value
    if property_type.value == DEVPROP_TYPE_STRING_LIST:
        return ctypes.wstring_at(buffer, buffer_size.value // 2).rstrip('\0').split('\0')
    if property_type.value == DEVPROP_TYPE_BINARY:
        return buffer
    raise NotImplementedError('DEVPROPTYPE {} is not implemented!'.format(property_type.value))


class cached_property:
    # Decorator (non-data) for building an attribute on-demand on first use.
    def __init__(self, function):
        self.__attr_name = function.__name__
        self.__function = function

    def __get__(self, instance, owner):
        attr = self.__function(instance)
        setattr(instance, self.__attr_name, attr)
        return attr


class DeviceNode:
    def __init__(self, instance_handle):
        self.__instance_handle = instance_handle

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.__instance_handle == other.__instance_handle

    def __lt__(self, other):
        return self.__instance_handle < other.__instance_handle

    def __hash__(self):
        return hash(self.__instance_handle)

    @property
    def instance_handle(self):
        return self.__instance_handle

    @cached_property
    def instance_identifier(self):
        return self.get_property(DEVPKEY_Device_InstanceId)

    @property
    def status(self):
        node_status = ctypes.c_uint32()
        problem_number = ctypes.c_uint32()
        cr = CM_Get_DevNode_Status(ctypes.byref(node_status), ctypes.byref(problem_number), self.__instance_handle, 0)
        if cr != CR_SUCCESS:
            return None
        return node_status, problem_number

    @cached_property
    def parent(self):
        parent_instance_handle = ctypes.c_uint32()
        cr = CM_Get_Parent(ctypes.byref(parent_instance_handle), self.__instance_handle, 0)
        if cr != CR_SUCCESS:
            return None
        return DeviceNode(parent_instance_handle.value)

    @cached_property
    def name(self):
        return self.get_property(DEVPKEY_NAME)

    @cached_property
    def description(self):
        return self.get_property(DEVPKEY_Device_DeviceDesc)

    @cached_property
    def manufacturer(self):
        return self.get_property(DEVPKEY_Device_Manufacturer)

    @cached_property
    def address(self):
        return self.get_property(DEVPKEY_Device_Address)

    @cached_property
    def bus_reported_device_description(self):
        return self.get_property(DEVPKEY_Device_BusReportedDeviceDesc)

    @cached_property
    def friendly_name(self):
        return self.get_property(DEVPKEY_Device_FriendlyName)

    @cached_property
    def location_paths(self):
        return self.get_property(DEVPKEY_Device_LocationPaths)

    @property
    def power_data(self):
        buffer = self.get_property(DEVPKEY_Device_PowerData)
        if buffer is None:
            return None
        return CM_POWER_DATA.from_buffer_copy(buffer)

    @cached_property
    def port_name(self):
        hkey = ctypes.c_void_p()
        cr = CM_Open_DevNode_Key(
            self.__instance_handle,
            KEY_READ,
            0,
            RegDisposition_OpenExisting,
            ctypes.byref(hkey),
            CM_REGISTRY_HARDWARE
        )
        if cr != CR_SUCCESS:
            return None
        buffer_size = ctypes.c_uint32()
        status = RegQueryValueExW(
            hkey,
            "PortName",
            None,
            None,
            None,
            ctypes.byref(buffer_size)
        )
        if (status != ERROR_SUCCESS) and (status != ERROR_MORE_DATA):
            return None
        buffer = ctypes.create_unicode_buffer(buffer_size.value // 2)
        status = RegQueryValueExW(
            hkey,
            "PortName",
            None,
            None,
            buffer,
            ctypes.byref(buffer_size)
        )
        if status != ERROR_SUCCESS:
            return None
        RegCloseKey(hkey)
        return buffer.value

    def get_property(self, property_key):
        buffer_size = ctypes.c_uint32()
        property_type = ctypes.c_uint32()
        cr = CM_Get_DevNode_PropertyW(
            self.__instance_handle,
            ctypes.byref(property_key),
            ctypes.byref(property_type),
            None,
            ctypes.byref(buffer_size),
            0
        )
        if cr != CR_BUFFER_SMALL and cr != CR_SUCCESS:
            return None
        buffer = ctypes.create_string_buffer(buffer_size.value)
        cr = CM_Get_DevNode_PropertyW(
                self.__instance_handle,
                ctypes.byref(property_key),
                ctypes.byref(property_type),
                buffer,
                ctypes.byref(buffer_size),
                0
        )
        if cr != CR_SUCCESS:
            return None
        return parse_device_property(buffer, buffer_size, property_type)


class DeviceInterface(DeviceNode):
    guid_list = []

    def __init__(self, interface):
        self.__interface = interface
        super(DeviceInterface, self).__init__(self.instance_handle)

    @classmethod
    def enumerate_device(cls):
        # Repeat for all possible GUIDs.
        for guid in cls.guid_list:
            device_interface_list_size = ctypes.c_uint32()
            cr = CM_Get_Device_Interface_List_SizeW(
                ctypes.byref(device_interface_list_size),
                ctypes.byref(guid),
                None,
                CM_GET_DEVICE_INTERFACE_LIST_PRESENT
            )
            if cr != CR_SUCCESS:
                raise ctypes.WinError(CM_MapCrToWin32Err(cr, 0))
            if device_interface_list_size.value > 1:
                device_interface_list = ctypes.create_unicode_buffer(device_interface_list_size.value)
                cr = CM_Get_Device_Interface_ListW(
                    ctypes.byref(guid),
                    None,
                    device_interface_list,
                    ctypes.sizeof(device_interface_list),
                    CM_GET_DEVICE_INTERFACE_LIST_PRESENT
                )
                if cr != CR_SUCCESS:
                    raise ctypes.WinError(CM_MapCrToWin32Err(cr, 0))
                null_terminated_list = ctypes.wstring_at(device_interface_list, device_interface_list_size.value)
                for interface in null_terminated_list.rstrip('\0').split('\0'):
                    yield cls(interface)

    @property
    def interface(self):
        return self.__interface

    @cached_property
    def instance_identifier(self):
        return self.get_interface_property(DEVPKEY_Device_InstanceId)

    @cached_property
    def instance_handle(self):
        instance_handle = ctypes.c_uint32()
        cr = CM_Locate_DevNodeW(
            ctypes.byref(instance_handle),
            self.instance_identifier,
            CM_LOCATE_DEVNODE_NORMAL
        )
        if cr != CR_SUCCESS:
            return None
        return instance_handle.value

    def get_interface_property(self, property_key):
        buffer_size = ctypes.c_uint32()
        property_type = ctypes.c_uint32()
        cr = CM_Get_Device_Interface_PropertyW(
            self.__interface,
            ctypes.byref(property_key),
            ctypes.byref(property_type),
            None,
            ctypes.byref(buffer_size),
            0
        )
        if cr != CR_BUFFER_SMALL and cr != CR_SUCCESS:
            return None
        buffer = ctypes.create_string_buffer(buffer_size.value)
        cr = CM_Get_Device_Interface_PropertyW(
                self.__interface,
                ctypes.byref(property_key),
                ctypes.byref(property_type),
                buffer,
                ctypes.byref(buffer_size),
                0
        )
        if cr != CR_SUCCESS:
            return None
        return parse_device_property(buffer, buffer_size, property_type)


class PortDevice(DeviceInterface):
    # Use GUID_DEVINTERFACE_COMPORT and GUID_DEVINTERFACE_MODEM instead of GUID_CLASS_COMPORT and GUID_CLASS_MODEM.
    # https://code.qt.io/cgit/qt/qtserialport.git/commit/?id=63bfe5ea4203af3c294691216ddfb7dc29f310f7
    guid_list = [
        GUID_DEVINTERFACE_COMPORT,
        GUID_DEVINTERFACE_MODEM
    ]

    def wake_up_device(self):
        # Trigger the port to wake up the usb device.
        port_handle = CreateFileW(
            self.interface,
            GENERIC_READ | GENERIC_WRITE,
            0,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            0
        )
        CloseHandle(port_handle)


class USBHostControllerDevice(DeviceInterface):
    guid_list = [GUID_DEVINTERFACE_USB_HOST_CONTROLLER]


class USBHubDevice(DeviceInterface):
    guid_list = [GUID_DEVINTERFACE_USB_HUB]


class DeviceRegistry:
    # Cached usb info.
    # As shown in the registry, COM number is binding to the interface string.
    # HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\COM Name Arbiter\Devices
    # So we use interface string as key to cache usb info.
    usb_info_cache_dict = {}

    def __init__(self, cache_usb_info=True):
        if not cache_usb_info:
            self.usb_info_cache_dict.clear()
        self.cache_usb_info = cache_usb_info
        # Make some preparations.
        self.all_usb_hubs = sorted(set(USBHubDevice.enumerate_device()))
        self.all_usb_host_controllers = sorted(set(USBHostControllerDevice.enumerate_device()))

    def get_location_string(self, usb_device, usb_host_controller, bConfigurationValue=None, bInterfaceNumber=None):
        # <bus>-<port[.port[.port]]>:<config>.<interface>
        location_paths = usb_device.location_paths
        if not location_paths:
            return None
        if (bConfigurationValue is None) and (bInterfaceNumber is not None):
            bConfigurationValue = 'x'
        location = [str(self.get_bus_number(usb_host_controller))]
        for g in re.finditer(r'#USB\((\w+)\)', location_paths[0]):
            if len(location) > 1:
                location.append('.')
            else:
                location.append('-')
            location.append(g.group(1))
        if bInterfaceNumber is not None:
            location.append(':{}.{}'.format(
                bConfigurationValue,
                bInterfaceNumber
            ))
        return ''.join(location)

    def get_bus_number(self, usb_host_controller):
        try:
            bus_number = self.all_usb_host_controllers.index(usb_host_controller) + 1
        except ValueError:
            bus_number = 0
        return bus_number

    def get_usb_info(self, port_device):
        # Check for usb_info in cache.
        if self.cache_usb_info:
            cache_key = port_device.interface.casefold()
            if cache_key in self.usb_info_cache_dict:
                return self.usb_info_cache_dict[cache_key]

        # Get parent hub device, usb device and interface device recursively.
        # hub_device -> usb_device -> usb_interface_device -> port_device
        usb_device = port_device
        usb_interface_device = port_device
        while True:
            parent_device = usb_device.parent
            if parent_device is None:
                return None
            hub_device = find_from_iterable(self.all_usb_hubs, parent_device)
            if hub_device is not None:
                break
            usb_interface_device = usb_device
            usb_device = parent_device

        # Get usb host controller.
        parent_device = hub_device
        while parent_device is not None:
            usb_host_controller_device = find_from_iterable(self.all_usb_host_controllers, parent_device)
            if usb_host_controller_device is not None:
                break
            parent_device = parent_device.parent
        else:
            return None

        # Check the power status of the usb device.
        power_data = usb_device.power_data
        if power_data is not None:
            if power_data.PD_MostRecentPowerState != 1:
                # The device is in sleep state. It needs to be woken up to D0 state to get the usb description.
                port_device.wake_up_device()

        # Get the port number that the usb device is connected to.
        # https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-address
        usb_hub_port = usb_device.address
        if usb_hub_port is None:
            return None

        # Open the usb hub to send device io control request.
        with USBHubDeviceIOControl(hub_device.interface) as hub_io:
            # Somehow cannot open the usb hub.
            if not hub_io.is_open:
                return None

            # Request usb device connection info.
            connection_info = hub_io.request_usb_connection_info(usb_hub_port)
            if connection_info is None:
                # Fallback to request usb device description.
                device_description = hub_io.request_usb_device_description(usb_hub_port)
                if device_description is None:
                    # We can't get any information.
                    return None
            else:
                device_description = connection_info.DeviceDescriptor

            # Get product identifier and vendor identifier.
            pid = device_description.idProduct
            vid = device_description.idVendor

            # Request string description at iProduct, iManufacturer and iSerialNumber.
            language_id = hub_io.suggest_language_id(usb_hub_port)
            product = hub_io.request_usb_string_description(usb_hub_port, device_description.iProduct, language_id)
            manufacturer = hub_io.request_usb_string_description(usb_hub_port, device_description.iManufacturer, language_id)
            serial_number = hub_io.request_usb_string_description(usb_hub_port, device_description.iSerialNumber, language_id)

            # Get the bConfigurationValue.
            bConfigurationValue = None
            if connection_info is not None:
                # Get bConfigurationValue from device connection info.
                bConfigurationValue = connection_info.CurrentConfigurationValue
            elif device_description.bNumConfigurations == 1:
                # Mostly, there is only one Configuration, and bConfigurationValue is equal to 1.
                bConfigurationValue = 1

            # Get the bInterfaceNumber.
            bInterfaceNumber = None
            location_paths = usb_interface_device.location_paths
            if location_paths is not None:
                # Parse interface number from location paths.
                for p in location_paths:
                    # Find the #USBMI(?) patten in the last part of location string.
                    m = re.fullmatch(r'.*?#USBMI\((\d+)\)', p, re.IGNORECASE)
                    if m is not None:
                        bInterfaceNumber = int(m.group(1))
                        break
            else:
                # Try to parse interface number from instance identifier string.
                # https://learn.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
                # USB example: USB\VID_303A&PID_4001&MI_00\6&182C0AC9&0&0000
                m = re.fullmatch(
                    r'USB\\VID_[0-9a-f]{4}&PID_[0-9a-f]{4}&MI_(\d{2})\\.*?',
                    usb_interface_device.instance_identifier,
                    re.IGNORECASE
                )
                if m is not None:
                    bInterfaceNumber = int(m.group(1))

            # Read interface description.
            function = None
            interface = None
            if bConfigurationValue is not None:
                configuration_description = hub_io.request_usb_configuration_description(usb_hub_port, bConfigurationValue)
                if configuration_description is not None:
                    if device_description.bNumConfigurations == 1 and configuration_description.bNumInterfaces == 1:
                        # Usb device with single interface.
                        bInterfaceNumber = None  # Set to None to distinguish composite devices.
                    # Get interface string of bInterfaceNumber.
                    # There is only one alternative interface in most cases (bAlternateSetting == 0).
                    # If we don't know bAlternateSetting, then use the default interface.
                    interface_association_description, interface_description = \
                        hub_io.request_usb_interface_descriptions(
                            usb_hub_port,
                            configuration_description,
                            bInterfaceNumber
                        )
                    if interface_association_description is not None:
                        function = hub_io.request_usb_string_description(
                            usb_hub_port,
                            interface_association_description.iFunction,
                            language_id
                        )
                    if interface_description is not None:
                        interface = hub_io.request_usb_string_description(
                            usb_hub_port,
                            interface_description.iInterface,
                            language_id
                        )

        # Generate location string compatible with linux usbfs.
        location = self.get_location_string(
            usb_device,
            usb_host_controller_device,
            bConfigurationValue,
            bInterfaceNumber
        )

        usb_info = USBInfo(pid, vid, product, manufacturer, serial_number, location, function, interface)

        # Cache usb info.
        if self.cache_usb_info:
            self.usb_info_cache_dict[cache_key] = usb_info

        return usb_info


class USBHubDeviceIOControl:
    def __init__(self, device_path):
        self.device_path = device_path
        self.device_handle = INVALID_HANDLE_VALUE

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def is_open(self):
        return self.device_handle != INVALID_HANDLE_VALUE

    def open(self):
        self.device_handle = CreateFileW(
            self.device_path,
            GENERIC_WRITE,
            2,
            None,
            OPEN_EXISTING,
            0,
            None
        )

    def close(self):
        CloseHandle(self.device_handle)

    def request_supported_languages(self, usb_hub_port):
        # Filling setup package.
        description_request_buffer = ctypes.create_string_buffer(
            ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + ctypes.sizeof(USB_STRING_DESCRIPTOR)
        )
        description_request = ctypes.cast(description_request_buffer, ctypes.POINTER(USB_DESCRIPTOR_REQUEST))
        description_request.contents.ConnectionIndex = usb_hub_port
        description_request.contents.SetupPacket.wValue = USB_STRING_DESCRIPTOR_TYPE << 8
        description_request.contents.SetupPacket.wIndex = 0
        description_request.contents.SetupPacket.wLength = \
            ctypes.sizeof(description_request_buffer) - ctypes.sizeof(USB_DESCRIPTOR_REQUEST)

        # Send string description request.
        returned_size = ctypes.c_uint32()
        if not DeviceIoControl(
                self.device_handle,
                IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,
                description_request_buffer,
                ctypes.sizeof(description_request_buffer),
                description_request_buffer,
                ctypes.sizeof(description_request_buffer),
                ctypes.byref(returned_size),
                None
        ):
            return None

        # Parse string description from wstring buffer.
        description = ctypes.cast(
            ctypes.byref(description_request_buffer, ctypes.sizeof(USB_DESCRIPTOR_REQUEST)),
            ctypes.POINTER(USB_STRING_DESCRIPTOR)
        )

        # Check size again
        string_descriptor_size = returned_size.value - ctypes.sizeof(USB_DESCRIPTOR_REQUEST)
        if string_descriptor_size != description.contents.bLength:
            return None

        # Parse available language id
        available_language_id_count = (string_descriptor_size - 2) // 2
        languages = []
        for i in range(available_language_id_count):
            languages.append(ctypes.c_uint16.from_buffer(
                description_request_buffer,
                ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + i * 2 + 2
            ).value)
        return languages

    def suggest_language_id(self, usb_hub_port):
        available_languages = self.request_supported_languages(usb_hub_port)
        if not available_languages:
            return 0x0409
        default_language = GetUserDefaultLangID()
        if default_language in available_languages:
            return default_language
        else:
            return available_languages[0]

    def request_usb_string_description(self, usb_hub_port, string_index, langid=None):
        if string_index == 0:
            # There is no string description at this index.
            return None

        # Get a list of supported languages from index 0, and match langid to system default language.
        if langid is None:
            langid = self.suggest_language_id(usb_hub_port)

        # Filling setup package.
        description_request_buffer = \
            ctypes.create_string_buffer(ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + ctypes.sizeof(USB_STRING_DESCRIPTOR))
        description_request = ctypes.cast(description_request_buffer, ctypes.POINTER(USB_DESCRIPTOR_REQUEST))
        description_request.contents.ConnectionIndex = usb_hub_port
        description_request.contents.SetupPacket.wValue = (USB_STRING_DESCRIPTOR_TYPE << 8) | string_index
        description_request.contents.SetupPacket.wIndex = langid
        description_request.contents.SetupPacket.wLength = \
            ctypes.sizeof(description_request_buffer) - ctypes.sizeof(USB_DESCRIPTOR_REQUEST)

        # Send string description request.
        returned_size = ctypes.c_uint32()
        if not DeviceIoControl(
                self.device_handle,
                IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,
                description_request_buffer,
                ctypes.sizeof(description_request_buffer),
                description_request_buffer,
                ctypes.sizeof(description_request_buffer),
                ctypes.byref(returned_size),
                None
        ):
            return None

        # Parse string description from wstring buffer.
        description = ctypes.cast(
            ctypes.byref(description_request_buffer, ctypes.sizeof(USB_DESCRIPTOR_REQUEST)),
            ctypes.POINTER(USB_STRING_DESCRIPTOR)
        )

        # Convert wstring to python str.
        # Very few devices will have an extra null at the end of string, strip it.
        return ctypes.wstring_at(description.contents.bString, description.contents.bLength // 2 - 1).rstrip('\0')

    def request_usb_device_description(self, usb_hub_port):
        # Filling setup package for requesting device description.
        device_description_request_buffer = ctypes.create_string_buffer(
            ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + ctypes.sizeof(USB_DEVICE_DESCRIPTOR)
        )
        device_description_request = ctypes.cast(
            device_description_request_buffer,
            ctypes.POINTER(USB_DESCRIPTOR_REQUEST)
        )
        device_description_request.contents.ConnectionIndex = usb_hub_port
        device_description_request.contents.SetupPacket.bmRequest = 0x80
        device_description_request.contents.SetupPacket.bRequest = USB_REQUEST_GET_DESCRIPTOR
        device_description_request.contents.SetupPacket.wValue = USB_DEVICE_DESCRIPTOR_TYPE << 8
        device_description_request.contents.SetupPacket.wLength = ctypes.sizeof(USB_DEVICE_DESCRIPTOR)

        # Send usb device description request.
        returned_size = ctypes.c_uint32()
        if not DeviceIoControl(
                self.device_handle,
                IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,
                device_description_request_buffer,
                ctypes.sizeof(device_description_request_buffer),
                device_description_request_buffer,
                ctypes.sizeof(device_description_request_buffer),
                ctypes.byref(returned_size),
                None
        ):
            return None

        # Get device description.
        return USB_DEVICE_DESCRIPTOR.from_buffer_copy(
            device_description_request_buffer,
            ctypes.sizeof(USB_DESCRIPTOR_REQUEST)
        )

    def request_usb_configuration_description(self, usb_hub_port, bConfigurationValue):
        # Filling setup package for requesting configuration description.
        configuration_description_request_buffer = ctypes.create_string_buffer(
            ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + ctypes.sizeof(USB_CONFIGURATION_DESCRIPTOR)
        )
        configuration_description_request = ctypes.cast(
            configuration_description_request_buffer,
            ctypes.POINTER(USB_DESCRIPTOR_REQUEST)
        )
        configuration_description_request.contents.ConnectionIndex = usb_hub_port
        configuration_description_request.contents.SetupPacket.bmRequest = 0x80
        configuration_description_request.contents.SetupPacket.bRequest = USB_REQUEST_GET_DESCRIPTOR
        configuration_description_request.contents.SetupPacket.wValue = \
            (USB_CONFIGURATION_DESCRIPTOR_TYPE << 8) | (bConfigurationValue - 1)
        configuration_description_request.contents.SetupPacket.wLength = ctypes.sizeof(USB_CONFIGURATION_DESCRIPTOR)

        # Send usb configuration description request.
        returned_size = ctypes.c_uint32()
        if not DeviceIoControl(
                self.device_handle,
                IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,
                configuration_description_request_buffer,
                ctypes.sizeof(configuration_description_request_buffer),
                configuration_description_request_buffer,
                ctypes.sizeof(configuration_description_request_buffer),
                ctypes.byref(returned_size),
                None
        ):
            return None

        # Get configuration description.
        return USB_CONFIGURATION_DESCRIPTOR.from_buffer_copy(
            configuration_description_request_buffer,
            ctypes.sizeof(USB_DESCRIPTOR_REQUEST)
        )

    def request_usb_interface_descriptions(self, usb_hub_port, configuration_description, bInterfaceNumber, bAlternateSetting=0):
        # Single interface usb device.
        if bInterfaceNumber is None:
            bInterfaceNumber = 0

        # Now request the entire Configuration Descriptor using a dynamically
        # allocated buffer which is sized big enough to hold the entire descriptor
        configuration_description_request_buffer = ctypes.create_string_buffer(
            ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + configuration_description.wTotalLength
        )
        configuration_description_request = ctypes.cast(
            configuration_description_request_buffer,
            ctypes.POINTER(USB_DESCRIPTOR_REQUEST)
        )
        configuration_description_request.contents.ConnectionIndex = usb_hub_port
        configuration_description_request.contents.SetupPacket.bmRequest = 0x80
        configuration_description_request.contents.SetupPacket.bRequest = USB_REQUEST_GET_DESCRIPTOR
        configuration_description_request.contents.SetupPacket.wValue = \
            (USB_CONFIGURATION_DESCRIPTOR_TYPE << 8) | (configuration_description.bConfigurationValue - 1)
        configuration_description_request.contents.SetupPacket.wLength = configuration_description.wTotalLength

        # Send usb configuration description request.
        returned_size = ctypes.c_uint32()
        if not DeviceIoControl(
                self.device_handle,
                IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,
                configuration_description_request_buffer,
                ctypes.sizeof(configuration_description_request_buffer),
                configuration_description_request_buffer,
                ctypes.sizeof(configuration_description_request_buffer),
                ctypes.byref(returned_size),
                None
        ):
            return None

        # https://github.com/microsoft/Windows-driver-samples/blob/main/usb/usbview/enum.c#L2413
        common_description_offset = 0
        target_interface_association_description = None
        target_interface_description = None
        while True:
            if common_description_offset + ctypes.sizeof(USB_COMMON_DESCRIPTOR) \
                    < configuration_description.wTotalLength:
                common_description = ctypes.cast(
                    ctypes.byref(
                        configuration_description_request_buffer,
                        ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + common_description_offset
                    ),
                    ctypes.POINTER(USB_COMMON_DESCRIPTOR)
                )
                if common_description_offset + common_description.contents.bLength \
                        <= configuration_description.wTotalLength:

                    # Interface association description for iFunction
                    if common_description.contents.bDescriptorType == USB_INTERFACE_ASSOCIATION_DESCRIPTOR_TYPE:
                        if common_description.contents.bLength == ctypes.sizeof(USB_INTERFACE_ASSOCIATION_DESCRIPTOR):
                            interface_association_description = ctypes.cast(
                                ctypes.byref(
                                    configuration_description_request_buffer,
                                    ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + common_description_offset
                                ),
                                ctypes.POINTER(USB_INTERFACE_ASSOCIATION_DESCRIPTOR)
                            )
                            if interface_association_description.contents.bFirstInterface \
                                    <= bInterfaceNumber \
                                    <= interface_association_description.contents.bFirstInterface \
                                    + interface_association_description.contents.bInterfaceCount - 1:
                                target_interface_association_description = \
                                    USB_INTERFACE_ASSOCIATION_DESCRIPTOR.from_buffer_copy(
                                        configuration_description_request_buffer,
                                        ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + common_description_offset
                                    )
                        else:
                            break

                    # Interface description for iInterface
                    if common_description.contents.bDescriptorType == USB_INTERFACE_DESCRIPTOR_TYPE:
                        if common_description.contents.bLength == ctypes.sizeof(USB_INTERFACE_DESCRIPTOR):
                            interface_description = ctypes.cast(
                                ctypes.byref(
                                    configuration_description_request_buffer,
                                    ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + common_description_offset
                                ),
                                ctypes.POINTER(USB_INTERFACE_DESCRIPTOR)
                            )
                            if interface_description.contents.bInterfaceNumber == bInterfaceNumber \
                                    and interface_description.contents.bAlternateSetting == bAlternateSetting:
                                target_interface_description = USB_INTERFACE_DESCRIPTOR.from_buffer_copy(
                                    configuration_description_request_buffer,
                                    ctypes.sizeof(USB_DESCRIPTOR_REQUEST) + common_description_offset
                                )
                        else:
                            break

                    # interface association description precedes interface description
                    # https://www.usb.org/sites/default/files/iadclasscode_r10.pdf figure 2-1
                    if target_interface_description is not None:
                        break

                    common_description_offset += common_description.contents.bLength
                else:
                    break
            else:
                break
        return target_interface_association_description, target_interface_description

    def request_usb_connection_info(self, usb_hub_port):
        connection_info = USB_NODE_CONNECTION_INFORMATION_EX()
        connection_info.ConnectionIndex = usb_hub_port
        returned_size = ctypes.c_uint32()
        if not DeviceIoControl(
                self.device_handle,
                IOCTL_USB_GET_NODE_CONNECTION_INFORMATION_EX,
                ctypes.byref(connection_info),
                ctypes.sizeof(USB_NODE_CONNECTION_INFORMATION_EX),
                ctypes.byref(connection_info),
                ctypes.sizeof(USB_NODE_CONNECTION_INFORMATION_EX),
                ctypes.byref(returned_size),
                None
        ):
            return None
        return connection_info


class USBInfo:
    def __init__(self, pid, vid, product, manufacturer, serial_number, location, function, interface):
        self.pid = pid
        self.vid = vid
        self.product = product
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.location = location
        self.function = function
        self.interface = interface


def iterate_comports(cache_usb_info=True):
    # Enumerate and store all connected usb hubs.
    device_registry = DeviceRegistry(cache_usb_info)

    # Generate non-repeating serial devices.
    yielded_devices = []

    # Iterate through each serial device.
    for port_device in PortDevice.enumerate_device():
        if port_device in yielded_devices:
            # Skip repeated serial device.
            continue
        yielded_devices.append(port_device)

        # Skip parallel ports.
        if port_device.port_name.startswith('LPT'):
            continue

        # Request usb information.
        usb_info = device_registry.get_usb_info(port_device)

        # Generate pyserial ListPortInfo
        info = ListPortInfo(port_device.port_name, skip_link_detection=True)
        if usb_info is None:
            # usb_info may be None because some serial ports are not usb interfaces (e.g. virtual serial ports).
            info.name = port_device.name
            info.hwid = port_device.instance_identifier
            info.manufacturer = port_device.manufacturer
            info.description = port_device.description
            info.interface = port_device.bus_reported_device_description
        else:
            info.name = port_device.name
            info.pid = usb_info.pid
            info.vid = usb_info.vid
            info.product = usb_info.product
            info.manufacturer = usb_info.manufacturer
            info.serial_number = usb_info.serial_number
            info.location = usb_info.location
            info.interface = usb_info.interface
            info.apply_usb_info()
        yield info


def comports(include_links=False):
    # Compatible with pyserial.
    return list(iterate_comports())


if __name__ == '__main__':
    for port, desc, hwid in sorted(comports()):
        print("{}: {} [{}]".format(port, desc, hwid))
