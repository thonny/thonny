# -*- coding: utf-8 -*-

import os.path
import platform
import queue
import shlex
import subprocess
import sys
import threading
import time
from typing import Optional, Sequence, Tuple

PASSWORD_METHOD = "password"
PUBLIC_KEY_NO_PASS_METHOD = "public-key (without passphrase)"
PUBLIC_KEY_WITH_PASS_METHOD = "public-key (with passphrase)"


def delete_dir_try_hard(path: str, hardness: int = 5) -> None:
    # Deleting the folder on Windows is not so easy task
    # http://bugs.python.org/issue15496
    import shutil

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
    return sys.platform == "win32"


def running_on_mac_os() -> bool:
    return sys.platform == "darwin"


def running_on_linux() -> bool:
    return sys.platform == "linux"


def running_on_rpi() -> bool:
    machine_lower = platform.uname().machine.lower()
    return running_on_linux() and (
        # not great heuristics, I know
        machine_lower.startswith("arm")
        or machine_lower.startswith("aarch64")
        or os.environ.get("DESKTOP_SESSION") == "LXDE-pi"
    )


def get_user_site_packages_dir_for_base(userbase: str) -> str:
    # copied from site._get_path of 3.8 and 3.10
    version = sys.version_info

    if os.name == "nt":
        if sys.version_info < (3, 10):
            return f"{userbase}\\Python{version[0]}{version[1]}\\site-packages"
        else:
            ver_nodot = sys.winver.replace(".", "")
            return f"{userbase}\\Python{ver_nodot}\\site-packages"

    if sys.platform == "darwin" and sys._framework:
        return f"{userbase}/lib/python/site-packages"

    return f"{userbase}/lib/python{version[0]}.{version[1]}/site-packages"


def list_volumes(skip_letters=set()) -> Sequence[str]:
    "Adapted from https://github.com/ntoll/uflash/blob/master/uflash.py"
    if sys.platform == "win32":
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
                if disk in skip_letters:
                    continue
                path = "{}:\\".format(disk)
                if os.path.exists(path):
                    volumes.append(path)

            return volumes
        finally:
            ctypes.windll.kernel32.SetErrorMode(old_mode)  # @UndefinedVariable
    if sys.platform == "linux":
        from dbus_next.errors import DBusError

        from thonny.udisks import list_volumes_sync

        mount_points = []
        try:
            mount_points = list_volumes_sync()
        except DBusError as error:
            # Fallback to using the 'mount' command on Linux if the Udisks D-Bus service is unavailable.
            if "org.freedesktop.DBus.Error.ServiceUnknown" not in error.text:
                raise
            mount_output = subprocess.check_output("mount").splitlines()
            mount_points = [x.split()[2].decode("utf-8") for x in mount_output]
        return mount_points
    else:
        # 'posix' means we're on *BSD or OSX (Mac).
        # Call the unix "mount" command to list the mounted volumes.
        mount_output = subprocess.check_output("mount").splitlines()
        return [x.split()[2].decode("utf-8") for x in mount_output]


def get_win_volume_name(path: str) -> str:
    """
    Each disk or external device connected to windows has an attribute
    called "volume name". This function returns the volume name for
    the given disk/device.
    Code from http://stackoverflow.com/a/12056414
    """
    if sys.platform == "win32":
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
    else:
        raise RuntimeError("Only meant for Windows")


def find_volumes_by_name(volume_name: str, skip_letters={"A"}) -> Sequence[str]:
    volumes = list_volumes(skip_letters=skip_letters)
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
    not_found_msg: Optional[str] = None,
    found_several_msg: Optional[str] = None,
    parent=None,
) -> Optional[str]:
    from thonny.languages import tr

    # Can't translate in the header as _ may not be available at import time
    if not_found_msg is None:
        not_found_msg = tr("Could not find disk '%s'. Do you want to locate it yourself?")

    if found_several_msg is None:
        found_several_msg = tr("Found several '%s' disks. Do you want to choose one yourself?")

    volumes = find_volumes_by_name(volume_name)
    if len(volumes) == 1:
        return volumes[0]
    else:
        if len(volumes) == 0:
            msg = not_found_msg % volume_name
        else:
            msg = found_several_msg % volume_name

        import tkinter as tk
        from tkinter.messagebox import askyesno

        from thonny.ui_utils import askdirectory

        if askyesno(tr("Can't find suitable disk"), msg, master=parent):
            path = askdirectory(parent=parent)
            if path:
                return path

    return None


def shorten_repr(original_repr: str, max_len: int = 1000) -> str:
    if len(original_repr) > max_len:
        return original_repr[: max_len - 1] + "…"
    else:
        return original_repr


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
        ret = GetProcessMemoryInfo(process, ctypes.byref(counters), ctypes.sizeof(counters))
        if not ret:
            raise ctypes.WinError()
        info = dict((name, getattr(counters, name)) for name, _ in counters._fields_)
        return info

    return get_memory_info()["PrivateUsage"]


def _unix_get_used_memory():
    # http://fa.bianp.net/blog/2013/different-ways-to-get-memory-consumption-or-lessons-learned-from-memory_profiler/
    "TODO:"


def construct_cmd_line(parts, safe_tokens=[]) -> str:
    def quote(s):
        if s in safe_tokens:
            return s
        else:
            return shlex.quote(s)

    return " ".join(map(quote, parts))


def user_friendly_python_command_line(cmd):
    if "-m" in cmd:
        cmd = cmd[cmd.index("-m") + 1 :]

    lines = [""]
    for item in cmd:
        if lines[-1] and len(lines[-1] + " " + item) > 60:
            lines.append("")
        lines[-1] = (lines[-1] + " " + item).strip()

    return "\n".join(lines)

    return subprocess.list2cmdline(cmd)


def parse_cmd_line(s):
    return shlex.split(s, posix=True)


def levenshtein_distance(s1, s2):
    # https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)  # pylint: disable=arguments-out-of-order

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
    transpositionRow = []
    prevRow = []

    #  build first leven matrix row
    #  The first row represents transformation from an empty string
    #  to the shorter string making it static [0-n]
    #  since this row is static we can set it as
    #  curRow and start computation at the second row or index 1
    curRow = list(range(0, l1 + 1))

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
            changeCost = prevRow[colNum - 1] + (0 if s1[colNum - 1] == s2[rowNum - 1] else 1)
            #  set the cell value - min distance to reach this
            #  position
            curRow[colNum] = min(insertionCost, deletionCost, changeCost)

            #  test for a possible transposition optimization
            #  check to see if we have at least 2 characters
            if 1 < rowNum <= colNum:
                #  test for possible transposition
                if s1[colNum - 1] == s2[colNum - 2] and s2[colNum - 1] == s1[colNum - 2]:
                    curRow[colNum] = min(curRow[colNum], transpositionRow[colNum - 2] + 1)

    #  the last cell of the matrix is ALWAYS the shortest distance between the two strings
    return curRow[-1]


def get_file_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if sys.platform == "win32":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


_timer_time = 0


def start_time(text=""):
    global _timer_time
    print("RESET", text)
    _timer_time = time.time()


def lap_time(text=""):
    global _timer_time
    new_time = time.time()
    print("LAP", text, round(new_time - _timer_time, 4))
    _timer_time = time.time()


def copy_to_clipboard(data):
    if running_on_windows():
        _copy_to_windows_clipboard(data)
    elif running_on_mac_os():
        command = ["pbcopy"]
    else:
        command = ["xsel", "-b", "-i"]

    env = dict(os.environ).copy()
    encoding = "utf-8"
    env["PYTHONIOENCODING"] = encoding

    if sys.version_info >= (3, 6):
        extra = {"encoding": encoding}
    else:
        extra = {}

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        shell=False,
        env=env,
        universal_newlines=True,
        close_fds=True,
        **extra,
    )
    proc.communicate(input=data, timeout=0.1)


def _copy_to_windows_clipboard(data):
    # https://bugs.python.org/file37366/test_clipboard_win.py
    import ctypes

    wcscpy = ctypes.cdll.msvcrt.wcscpy
    OpenClipboard = ctypes.windll.user32.OpenClipboard
    EmptyClipboard = ctypes.windll.user32.EmptyClipboard
    SetClipboardData = ctypes.windll.user32.SetClipboardData
    CloseClipboard = ctypes.windll.user32.CloseClipboard
    CF_UNICODETEXT = 13
    GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
    GlobalLock = ctypes.windll.kernel32.GlobalLock
    GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
    GMEM_DDESHARE = 0x2000

    OpenClipboard(None)
    EmptyClipboard()
    hCd = GlobalAlloc(GMEM_DDESHARE, 2 * (len(data) + 1))
    pchData = GlobalLock(hCd)
    wcscpy(ctypes.c_wchar_p(pchData), data)
    GlobalUnlock(hCd)
    SetClipboardData(CF_UNICODETEXT, hCd)
    # ctypes.windll.user32.SetClipboardText(CF_UNICODETEXT, hCd)
    CloseClipboard()


def sizeof_fmt(num, suffix="B"):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Unit suffix (optionnal) default = B
    :type suffix: str
    :rtype: str
    """
    # https://gist.github.com/cbwar/d2dfbc19b140bd599daccbe0fe925597
    for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            if unit == "":
                return "%d %s%s" % (num, unit, suffix)
            return "%.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


class PopenWithOutputQueues(subprocess.Popen):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()

        for stream, target_queue in [
            (self.stdout, self.stdout_queue),
            (self.stderr, self.stderr_queue),
        ]:
            threading.Thread(
                target=self._listen_thread, args=[stream, target_queue], daemon=True
            ).start()

    def _listen_thread(self, stream, target_queue: queue.Queue):
        while True:
            data = stream.readline()
            if data == "":
                break
            target_queue.put(data)


def inside_flatpak():
    import shutil

    return shutil.which("flatpak-spawn") and os.path.isfile("/app/manifest.json")


def show_command_not_available_in_flatpak_message():
    from tkinter import messagebox

    from thonny import get_workbench
    from thonny.languages import tr

    messagebox.showinfo(
        tr("Command not available"),
        tr("This command is not available if Thonny is run via Flatpak"),
        parent=get_workbench(),
    )
