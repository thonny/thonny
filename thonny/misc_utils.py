# -*- coding: utf-8 -*-

import os.path
import platform
import shlex
import shutil
import subprocess
import sys
import time
from typing import Optional, Sequence, Tuple

from thonny import get_workbench


def delete_dir_try_hard(path: str, hardness: int = 5) -> None:
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
        return bool(
            windll.kernel32.GetFileAttributesW(path)  # @UndefinedVariable
            & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
        )
    else:
        return False


def get_win_drives() -> Sequence[str]:
    # http://stackoverflow.com/a/2288225/261181
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa364939%28v=vs.85%29.aspx
    import string
    from ctypes import windll

    all_drive_types = [
        "DRIVE_UNKNOWN",
        "DRIVE_NO_ROOT_DIR",
        "DRIVE_REMOVABLE",
        "DRIVE_FIXED",
        "DRIVE_REMOTE",
        "DRIVE_CDROM",
        "DRIVE_RAMDISK",
    ]

    required_drive_types = [
        "DRIVE_REMOVABLE",
        "DRIVE_FIXED",
        "DRIVE_REMOTE",
        "DRIVE_RAMDISK",
    ]

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()  # @UndefinedVariable
    for letter in string.ascii_uppercase:
        drive_type = all_drive_types[
            windll.kernel32.GetDriveTypeW("%s:\\" % letter)
        ]  # @UndefinedVariable
        if bitmask & 1 and drive_type in required_drive_types:
            drives.append(letter + ":\\")
        bitmask >>= 1

    return drives


def list_volumes() -> Sequence[str]:
    "Adapted from https://github.com/ntoll/uflash/blob/master/uflash.py"
    if os.name == "posix":
        # 'posix' means we're on Linux or OSX (Mac).
        # Call the unix "mount" command to list the mounted volumes.
        mount_output = subprocess.check_output("mount").splitlines()
        return [x.split()[2].decode("utf-8") for x in mount_output]

    elif os.name == "nt":
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
            for disk in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                path = "{}:\\".format(disk)
                if os.path.exists(path):
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
        ctypes.c_wchar_p(path),
        vol_name_buf,
        ctypes.sizeof(vol_name_buf),
        None,
        None,
        None,
        None,
        0,
    )
    assert isinstance(vol_name_buf.value, str)
    return vol_name_buf.value


def find_volumes_by_name(volume_name: str) -> Sequence[str]:
    volumes = list_volumes()
    if os.name == "nt":
        return [
            volume
            for volume in volumes
            if get_win_volume_name(volume).upper() == volume_name.upper()
        ]
    else:
        return [volume for volume in volumes if volume.endswith(volume_name)]


def find_volume_by_name(
    volume_name: str,
    not_found_msg: str = "Could not find disk '%s'. Do you want to locate it yourself?",
    found_several_msg: str = "Found several '%s' disks. Do you want to choose one yourself?",
) -> Optional[str]:

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

        if askyesno("Can't find suitable disk", msg, parent=get_workbench()):
            path = askdirectory(master=get_workbench())
            if path:
                return path

    return None


def shorten_repr(original_repr: str, max_len: int = 1000) -> str:
    if len(original_repr) > max_len:
        return original_repr[: max_len - 1] + "…"
    else:
        return original_repr


def get_python_version_string(version_info: Optional[Tuple] = None) -> str:
    if version_info is None:
        version_info = sys.version_info

    result = ".".join(map(str, version_info[:3]))
    if version_info[3] != "final":
        result += "-" + version_info[3]

    result += " (" + ("64" if sys.maxsize > 2 ** 32 else "32") + " bit)\n"

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
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", SIZE_T),
            ("WorkingSetSize", SIZE_T),
            ("QuotaPeakPagedPoolUsage", SIZE_T),
            ("QuotaPagedPoolUsage", SIZE_T),
            ("QuotaPeakNonPagedPoolUsage", SIZE_T),
            ("QuotaNonPagedPoolUsage", SIZE_T),
            ("PagefileUsage", SIZE_T),
            ("PeakPagefileUsage", SIZE_T),
            ("PrivateUsage", SIZE_T),
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
        ret = GetProcessMemoryInfo(
            process, ctypes.byref(counters), ctypes.sizeof(counters)
        )
        if not ret:
            raise ctypes.WinError()
        info = dict((name, getattr(counters, name)) for name, _ in counters._fields_)
        return info

    return get_memory_info()["PrivateUsage"]


def _unix_get_used_memory():
    # http://fa.bianp.net/blog/2013/different-ways-to-get-memory-consumption-or-lessons-learned-from-memory_profiler/
    "TODO:"


def construct_cmd_line(parts):
    return " ".join(map(shlex.quote, parts))


def parse_cmd_line(s):
    return shlex.split(s, posix=True)


def levenshtein_distance(s1, s2):
    # https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = (
                previous_row[j + 1] + 1
            )  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def levenshtein_damerau_distance(s1, s2, maxDistance):
    # https://gist.github.com/giststhebearbear/4145811
    #  get smallest string so our rows are minimized
    s1, s2 = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
    #  set lengths
    l1, l2 = len(s1), len(s2)

    #  We are simulatng an NM matrix where n is the longer string
    #  and m is the shorter string. By doing this we can minimize
    #  memory usage to O(M).
    #  Since we are simulating the matrix we only maintain two rows
    #  at a time the current row and the previous rows.
    #  A move from the current cell looking at the cell before it indicates
    #  consideration of an insert operation.
    #  A move from the current cell looking at the cell above it indicates
    #  consideration of a deletion
    #  Both operations are cost 1
    #  A move from the current cell to the cell up and to the left indicates
    #  an edit operation of 0 cost for a matching character and a 1 cost for
    #  a non matching characters
    #  no row has been previously computed yet, set empty row
    #  Since this is also a Damerou-Levenshtein calculation transposition
    #  costs will be taken into account. These look back 2 characters to
    #  determine optimal cost based on a possible transposition
    #  example: aei -> aie with levensthein has a cost of 2
    #  match a, change e->i change i->e => aie
    #  Damarau-Levenshtein has a cost of 1
    #  match a, transpose ei to ie => aie
    transpositionRow = None
    prevRow = None

    #  build first leven matrix row
    #  The first row represents transformation from an empty string
    #  to the shorter string making it static [0-n]
    #  since this row is static we can set it as
    #  curRow and start computation at the second row or index 1
    curRow = [x for x in range(0, l1 + 1)]

    # use second length to loop through all the rows being built
    # we start at row one
    for rowNum in range(1, l2 + 1):
        #  set transposition, previous, and current
        #  because the rowNum always increments by one
        #  we can use rowNum to set the value representing
        #  the first column which is indicitive of transforming TO
        #  the empty string from our longer string
        #  transposition row maintains an extra row so that it is possible
        #  for us to apply Damarou's formula
        transpositionRow, prevRow, curRow = prevRow, curRow, [rowNum] + [0] * l1

        #  consider if we have passed the max distance if all paths through
        #  the transposition row are larger than the max we can stop calculating
        #  distance and return the last element in that row and return the max
        if transpositionRow:
            if not any(cellValue < maxDistance for cellValue in transpositionRow):
                return maxDistance

        for colNum in range(1, l1 + 1):
            insertionCost = curRow[colNum - 1] + 1
            deletionCost = prevRow[colNum] + 1
            changeCost = prevRow[colNum - 1] + (
                0 if s1[colNum - 1] == s2[rowNum - 1] else 1
            )
            #  set the cell value - min distance to reach this
            #  position
            curRow[colNum] = min(insertionCost, deletionCost, changeCost)

            #  test for a possible transposition optimization
            #  check to see if we have at least 2 characters
            if 1 < rowNum <= colNum:
                #  test for possible transposition
                if (
                    s1[colNum - 1] == s2[colNum - 2]
                    and s2[colNum - 1] == s1[colNum - 2]
                ):
                    curRow[colNum] = min(
                        curRow[colNum], transpositionRow[colNum - 2] + 1
                    )

    #  the last cell of the matrix is ALWAYS the shortest distance between the two strings
    return curRow[-1]


def get_file_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
