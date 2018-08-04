# -*- coding: utf-8 -*-

import os.path
import platform
import sys
import shutil
import time
import subprocess
from typing import Tuple, Sequence, Optional
import shlex
from thonny import get_workbench


def delete_dir_try_hard(path: str, hardness: int=5) -> None:
    # Deleting the folder on Windows is not so easy task
    # http://bugs.python.org/issue15496
    for i in range(hardness):
        if os.path.exists(path):
            time.sleep(i * 0.5)
            shutil.rmtree(path, True)
        else:
            break

    if os.path.exists(path):
        # try once more but now without ignoring errors
        shutil.rmtree(path, False)

def running_on_windows() -> bool:
    return platform.system() == "Windows"
    
def running_on_mac_os() -> bool:
    return platform.system() == "Darwin"
    
def running_on_linux() -> bool:
    return platform.system() == "Linux"

def is_hidden_or_system_file(path: str) -> bool:
    if os.path.basename(path).startswith("."):
        return True
    elif running_on_windows():
        from ctypes import windll
        FILE_ATTRIBUTE_HIDDEN = 0x2
        FILE_ATTRIBUTE_SYSTEM = 0x4
        return bool(windll.kernel32.GetFileAttributesW(path)  # @UndefinedVariable
                & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM))
    else:
        return False 
    
def get_win_drives() -> Sequence[str]:
    # http://stackoverflow.com/a/2288225/261181
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa364939%28v=vs.85%29.aspx
    import string
    from ctypes import windll
    
    all_drive_types = ['DRIVE_UNKNOWN', 
                       'DRIVE_NO_ROOT_DIR',
                       'DRIVE_REMOVABLE',
                       'DRIVE_FIXED',
                       'DRIVE_REMOTE',
                       'DRIVE_CDROM',
                       'DRIVE_RAMDISK']
    
    required_drive_types = ['DRIVE_REMOVABLE',
                            'DRIVE_FIXED',
                            'DRIVE_REMOTE',
                            'DRIVE_RAMDISK']

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()  # @UndefinedVariable
    for letter in string.ascii_uppercase:
        drive_type = all_drive_types[windll.kernel32.GetDriveTypeW("%s:\\" % letter)]  # @UndefinedVariable
        if bitmask & 1 and drive_type in required_drive_types:
            drives.append(letter + ":\\")
        bitmask >>= 1

    return drives

def list_volumes() -> Sequence[str]:
    "Adapted from https://github.com/ntoll/uflash/blob/master/uflash.py"
    if os.name == 'posix':
        # 'posix' means we're on Linux or OSX (Mac).
        # Call the unix "mount" command to list the mounted volumes.
        mount_output = subprocess.check_output('mount').splitlines()
        return [x.split()[2].decode("utf-8") for x in mount_output]
    
    elif os.name == 'nt':
        # 'nt' means we're on Windows.
        import ctypes

        #
        # In certain circumstances, volumes are allocated to USB
        # storage devices which cause a Windows popup to raise if their
        # volume contains no media. Wrapping the check in SetErrorMode
        # with SEM_FAILCRITICALERRORS (1) prevents this popup.
        #
        old_mode = ctypes.windll.kernel32.SetErrorMode(1)  # @UndefinedVariable
        try:
            volumes = []
            for disk in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                path = '{}:\\'.format(disk)
                if (os.path.exists(path)):
                    volumes.append(path)
            
            return volumes
        finally:
            ctypes.windll.kernel32.SetErrorMode(old_mode)  # @UndefinedVariable
    else:
        # No support for unknown operating systems.
        raise NotImplementedError('OS "{}" not supported.'.format(os.name))

def get_win_volume_name(path: str) -> str:
    """
    Each disk or external device connected to windows has an attribute
    called "volume name". This function returns the volume name for
    the given disk/device.
    Code from http://stackoverflow.com/a/12056414
    """
    import ctypes
    vol_name_buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.GetVolumeInformationW(  # @UndefinedVariable
        ctypes.c_wchar_p(path), vol_name_buf,
        ctypes.sizeof(vol_name_buf), None, None, None, None, 0)
    assert isinstance(vol_name_buf.value, str)
    return vol_name_buf.value


def find_volumes_by_name(volume_name: str) -> Sequence[str]:
    volumes = list_volumes()
    if os.name == "nt":
        return [volume for volume in volumes 
                if get_win_volume_name(volume).upper() == volume_name.upper()]
    else:
        return [volume for volume in volumes 
                if volume.endswith(volume_name)]

def find_volume_by_name(volume_name: str,
                        not_found_msg: str="Could not find disk '%s'. Do you want to locate it yourself?",
                        found_several_msg: str="Found several '%s' disks. Do you want to choose one yourself?") -> Optional[str]:
    
    volumes = find_volumes_by_name(volume_name)
    if len(volumes) == 1:
        return volumes[0]
    else:
        if len(volumes) == 0:
            msg = not_found_msg % volume_name
        else:
            msg = found_several_msg % volume_name
        
        from tkinter.messagebox import askyesno
        from thonny.ui_utils import askdirectory
        if askyesno("Can't find suitable disk", msg):
            path = askdirectory(master=get_workbench())
            if path:
                return path
    
    return None
            
            
            

def shorten_repr(original_repr: str, max_len: int=1000) -> str:
    if len(original_repr) > max_len:
        return original_repr[:max_len] + " ... [{} chars truncated]".format(len(original_repr) - max_len)
    else:
        return original_repr
        
def __maybe_later_get_thonny_data_folder():
    if running_on_windows():
        # CSIDL_LOCAL_APPDATA 
        # http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
        return os.path.join(__maybe_later_get_windows_special_folder(28), "Thonny")
    elif running_on_linux():
        # https://specifications.freedesktop.org/basedir-spec/latest/ar01s02.html
        # $XDG_DATA_HOME or $HOME/.local/share
        data_home = os.environ.get("XDG_DATA_HOME", 
                                   os.path.expanduser("~/.local/share"))
        return os.path.join(data_home, "Thonny") 
    elif running_on_mac_os():
        return os.path.expanduser("~/Library/Thonny")
    else:
        return os.path.expanduser("~/.thonny")

def __maybe_later_get_windows_special_folder(code):
    # http://stackoverflow.com/a/3859336/261181
    # http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
    import ctypes.wintypes
    SHGFP_TYPE_CURRENT= 0
    buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, code, 0, SHGFP_TYPE_CURRENT, buf)
    return buf.value

def get_python_version_string(version_info: Optional[Tuple] = None) -> str:
    if version_info is None:
        version_info = sys.version_info
         
    result = ".".join(map(str, version_info[:3]))
    if version_info[3] != "final":
        result += "-" + version_info[3]
    
    result += " (" + ("64" if sys.maxsize > 2**32 else "32")+ " bit)\n"
    
    return result    

def _win_get_used_memory():
    # http://code.activestate.com/recipes/578513-get-memory-usage-of-windows-processes-using-getpro/
    import ctypes
    from ctypes import wintypes
    
    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
    GetCurrentProcess.argtypes = []
    GetCurrentProcess.restype = wintypes.HANDLE
    
    SIZE_T = ctypes.c_size_t
    
    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        _fields_ = [
            ('cb', wintypes.DWORD),
            ('PageFaultCount', wintypes.DWORD),
            ('PeakWorkingSetSize', SIZE_T),
            ('WorkingSetSize', SIZE_T),
            ('QuotaPeakPagedPoolUsage', SIZE_T),
            ('QuotaPagedPoolUsage', SIZE_T),
            ('QuotaPeakNonPagedPoolUsage', SIZE_T),
            ('QuotaNonPagedPoolUsage', SIZE_T),
            ('PagefileUsage', SIZE_T),
            ('PeakPagefileUsage', SIZE_T),
            ('PrivateUsage', SIZE_T),
        ]
    
    GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
    GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
        wintypes.DWORD,
    ]
    GetProcessMemoryInfo.restype = wintypes.BOOL
    
    def get_current_process():
        """Return handle to current process."""
        return GetCurrentProcess()
    
    def get_memory_info(process=None):
        """Return Win32 process memory counters structure as a dict."""
        if process is None:
            process = get_current_process()
        counters = PROCESS_MEMORY_COUNTERS_EX()
        ret = GetProcessMemoryInfo(process, ctypes.byref(counters),
                                   ctypes.sizeof(counters))
        if not ret:
            raise ctypes.WinError()
        info = dict((name, getattr(counters, name))
                    for name, _ in counters._fields_)
        return info
    
    return get_memory_info()['PrivateUsage']

def _unix_get_used_memory():
    # http://fa.bianp.net/blog/2013/different-ways-to-get-memory-consumption-or-lessons-learned-from-memory_profiler/
    "TODO:"

def construct_cmd_line(parts):
    return " ".join(map(shlex.quote, parts))

def parse_cmd_line(s):
    return shlex.split(s, posix=True)

