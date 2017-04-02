# -*- coding: utf-8 -*-

import os.path
import platform
import sys
import shutil
import time


def eqfn(name1, name2):
    return os.path.normcase(name1) == os.path.normcase(name2)

def delete_dir_try_hard(path, hardness=5):
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

def running_on_windows():
    return platform.system() == "Windows"
    
def running_on_mac_os():
    return platform.system() == "Darwin"
    
def running_on_linux():
    return platform.system() == "Linux"

def is_hidden_or_system_file(path):
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
    
def get_win_drives():
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



def shorten_repr(original_repr, max_len=1000):
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

def get_python_version_string(version_info=None):
    if version_info == None:
        version_info = sys.version_info
         
    result = ".".join(map(str, version_info[:3]))
    if version_info[3] != "final":
        result += "-" + version_info[3]
    
    result += " (" + ("64" if sys.maxsize > 2**32 else "32")+ " bit)\n"
    
    return result    

