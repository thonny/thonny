# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime
import os.path
import pathlib
import platform
import queue
import shlex
import subprocess
import sys
import threading
import time
import urllib.parse
from logging import getLogger
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import unquote

from thonny import get_runner
from thonny.languages import tr

PASSWORD_METHOD = "password"
PUBLIC_KEY_NO_PASS_METHOD = "public-key (without passphrase)"
PUBLIC_KEY_WITH_PASS_METHOD = "public-key (with passphrase)"

FILE_URI_SCHEME: str = "file"
REMOTE_URI_SCHEME: str = "remote"
UNTITLED_URI_SCHEME: str = "untitled"
PLACEHOLDER_URI = f"{UNTITLED_URI_SCHEME}:0"

REMOTE_PATH_MARKER = " :: "

PROJECT_MARKERS = ["pyproject.toml", "setup.cfg", "setup.py", ".python-version", "Pipfile"]


logger = getLogger(__name__)


def get_known_folder(ID):
    # http://stackoverflow.com/a/3859336/261181
    # https://tarma.com/support/im9/using/symbols/functions/csidls.htm
    import ctypes.wintypes

    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, ID, 0, SHGFP_TYPE_CURRENT, buf)
    assert buf.value
    return buf.value


def get_roaming_appdata_dir():
    return get_known_folder(26)


def get_local_appdata_dir():
    return get_known_folder(28)


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
        or os.environ.get("DESKTOP_SESSION") == "LXDE-pi-wayfire"
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
        try:
            from dbus_next.errors import DBusError
        except ImportError:
            logger.info("Could not import dbus_next, falling back to mount command")
            return list_volumes_with_mount_command()

        from thonny.udisks import list_volumes_sync

        try:
            return list_volumes_sync()
        except DBusError as error:
            if "org.freedesktop.DBus.Error.ServiceUnknown" not in error.text:
                raise
            # Fallback to using the 'mount' command on Linux if the Udisks D-Bus service is unavailable.
            return list_volumes_with_mount_command()
    else:
        # 'posix' means we're on *BSD or OSX (Mac).
        # Call the unix "mount" command to list the mounted volumes.
        return list_volumes_with_mount_command()


def list_volumes_with_mount_command() -> Sequence[str]:
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


def jaro_similarity(s, t):
    """Jaro distance between two strings."""
    # Source: https://rosettacode.org/wiki/Jaro_similarity
    s_len = len(s)
    t_len = len(t)

    if s_len == 0 and t_len == 0:
        return 1

    match_distance = (max(s_len, t_len) // 2) - 1

    s_matches = [False] * s_len
    t_matches = [False] * t_len

    matches = 0
    transpositions = 0

    for i in range(s_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, t_len)

        for j in range(start, end):
            if t_matches[j]:
                continue
            if s[i] != t[j]:
                continue
            s_matches[i] = True
            t_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0

    k = 0
    for i in range(s_len):
        if not s_matches[i]:
            continue
        while not t_matches[k]:
            k += 1
        if s[i] != t[k]:
            transpositions += 1
        k += 1

    return ((matches / s_len) + (matches / t_len) + ((matches - transpositions / 2) / matches)) / 3


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


def get_menu_char():
    if running_on_windows():
        return "≡"  # Identical to
    else:
        return "☰"  # Trigram for heaven, too heavy on Windows


def download_bytes(url: str, timeout: int = 10) -> bytes:
    from urllib.request import Request, urlopen

    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
        },
    )
    with urlopen(req, timeout=timeout) as fp:
        if fp.info().get("Content-Encoding") == "gzip":
            import gzip

            return gzip.decompress(fp.read())
        else:
            return fp.read()


def download_and_parse_json(url: str, timeout: int = 10) -> Any:
    import json

    return json.loads(download_bytes(url, timeout=timeout))


def post_and_return_stream(
    url: str, data: Any, headers: Dict[str, Any] = {}, timeout: int = 10
) -> Any:
    import json
    from urllib.request import Request, urlopen

    if not isinstance(data, bytes):
        if isinstance(data, str):
            data = data.encode(encoding="utf-8")
        else:
            data = json.dumps(data).encode(encoding="utf-8")

    req = Request(url, headers={key: str(value) for key, value in headers.items()})

    return urlopen(req, data=data, timeout=timeout)


def post_and_parse_json(
    url: str, data: Any, headers: Dict[str, Any] = {}, timeout: int = 10
) -> Any:
    import json

    resp = post_and_return_stream(
        url, data=data, headers={key: str(value) for key, value in headers.items()}, timeout=timeout
    )
    return json.load(resp)


def get_and_parse_json(url: str, headers: Dict[str, Any] = {}, timeout: int = 10) -> Any:
    import json
    from urllib.request import Request, urlopen

    req = Request(url, headers=headers)

    resp = urlopen(req, timeout=timeout)
    return json.load(resp)


def get_os_level_favorite_folders() -> List[str]:
    if running_on_windows():
        raise NotImplementedError()

    result = []
    for name in [".", "Desktop", "Documents", "Downloads"]:
        path = os.path.realpath(os.path.expanduser(f"~/{name}"))
        if os.path.isdir(path):
            result.append(path)

    gtk_favorites_path = os.path.expanduser("~/.config/gtk-3.0/bookmarks")
    if running_on_linux() and os.path.isfile(gtk_favorites_path):
        with open(gtk_favorites_path, "rt", encoding="utf-8") as fp:
            for line in fp:
                if line.startswith("file:///"):
                    path = line[7:].strip()
                    if os.path.isdir(path) and path not in result:
                        result.append(path)

    return result


def format_date_and_time_compact(
    timestamp: time.struct_time, without_seconds: bool, optimize_year: bool = False
):
    return (
        format_date_compact(timestamp, optimize_year=optimize_year)
        + " • "
        + format_time_compact(timestamp, without_seconds=without_seconds)
    )


def format_time_compact(timestamp: time.struct_time, without_seconds: bool):

    # Useful with locale specific formats, which would be a hassle to construct from parts
    s = time.strftime("%X", timestamp)
    if without_seconds:
        seconds_part = ":%02d" % (timestamp.tm_sec,)
        seconds_index = s.rfind(seconds_part)
        if seconds_index == -1:
            return s

        return s[:seconds_index] + s[seconds_index + len(seconds_part) :]
    else:
        return s


def format_date_compact(timestamp: time.struct_time, optimize_year: bool = False):
    # Useful with locale specific formats, which would be a hassle to construct from parts
    now = time.localtime()
    if (
        timestamp.tm_year == now.tm_year
        and timestamp.tm_mon == now.tm_mon
        and timestamp.tm_mday == now.tm_mday
    ):
        return tr("Today")

    result = time.strftime(get_date_format_with_month_abbrev(), timestamp)
    age_in_days = (time.time() - time.mktime(timestamp)) / 60 / 60 / 24
    if (
        age_in_days < 0
        or (now.tm_year != timestamp.tm_year and age_in_days > 10)
        or age_in_days > 10
    ):
        result += " " + str(timestamp.tm_year)

    return result


_date_format_with_month_abbrev = None


def get_date_format_with_month_abbrev() -> str:
    global _date_format_with_month_abbrev
    if _date_format_with_month_abbrev is None:
        _date_format_with_month_abbrev = _compute_date_format_with_month_abbrev()
    return _date_format_with_month_abbrev


def _compute_date_format_with_month_abbrev():
    # %x does not use month abbreviation, i.e. it may be confusing
    # %c has too many fields
    # Need to find out, whether current locale uses
    #  - day before or after month
    #  - with period or without
    #  - with leading zero or without

    fallback_format = "%d %b"
    ref_year = 2021
    ref_month = 12
    ref_day = 3
    ref_timestamp = (ref_year, ref_month, ref_day, 0, 0, 0, 0, 0, 0)
    month_abbrev: str = time.strftime("%b", ref_timestamp)
    parts = time.strftime("%c", ref_timestamp).split()

    for i, part in enumerate(parts):
        if str(ref_day) in part:
            day_index = i
            if part.startswith("0"):
                day_fmt = "%d"
            elif running_on_windows():
                day_fmt = "%#d"  # without leading zero
            else:
                day_fmt = "%-d"  # without leading zero

            if part.endswith("."):
                day_fmt += "."
            break
    else:
        return fallback_format

    for i, part in enumerate(parts):
        if month_abbrev.lower() in part.lower():
            month_index = i
            if part.endswith("/"):
                # ja_JP and ko_KR
                month_fmt = "%b/"
            else:
                month_fmt = "%b"
            break
    else:
        return fallback_format

    if month_index < day_index:
        return f"{month_fmt} {day_fmt}"
    else:
        return f"{day_fmt} {month_fmt}"


def version_str_to_tuple_of_ints(s: str) -> Tuple[int]:
    parts = s.split(".")
    return tuple([int(part) for part in parts if part.isnumeric()])


def uri_to_target_path(uri: str) -> str:
    parts = urllib.parse.urlsplit(uri)
    if parts.scheme == UNTITLED_URI_SCHEME:
        raise ValueError("Can't get path of untitled uri")

    elif parts.scheme == FILE_URI_SCHEME:
        if parts.netloc:
            # assuming Windows UNC
            return f"//{parts.netloc}{unquote(parts.path)}"

        path = unquote(parts.path)
        if path.startswith("/") and path[2:3] == ":":
            # Windows path
            return path[1:].replace("/", "\\")
        else:
            return path

    elif parts.scheme == REMOTE_URI_SCHEME:
        return unquote(parts.path)

    else:
        raise ValueError(f"Unsupported URI scheme '{parts.scheme}'")


def legacy_remote_filename_to_target_path(s) -> str:
    assert is_legacy_remote_filename(s)
    return s[s.find(REMOTE_PATH_MARKER) + len(REMOTE_PATH_MARKER) :]


def is_legacy_remote_filename(s: str) -> bool:
    return REMOTE_PATH_MARKER in s


def is_local_path(s: str) -> bool:
    return (
        not is_legacy_remote_filename(s)
        and not s.startswith("<")
        and (s.startswith("/") or s[1:3] == ":\\")
    )


def uri_to_legacy_filename(uri: str) -> str:
    """Returns 'blah :: /path/file' for remote files, as was common in Thonny 4"""
    if is_remote_uri(uri):
        return make_legacy_remote_path(uri_to_target_path(uri))
    else:
        return uri_to_target_path(uri)


def ensure_uri(filename_or_uri: str) -> str:
    if is_legacy_remote_filename(filename_or_uri):
        return legacy_filename_to_uri(filename_or_uri)
    elif is_local_path(filename_or_uri):
        return local_path_to_uri(filename_or_uri)
    elif ":" in filename_or_uri:
        return filename_or_uri
    else:
        raise ValueError(f"Can't understand filename or uri: {filename_or_uri!r}")


def legacy_filename_to_uri(filename: str) -> str:
    if is_legacy_remote_filename(filename):
        return remote_path_to_uri(legacy_remote_filename_to_target_path(filename))
    else:
        return local_path_to_uri(filename)


def uri_to_long_title(uri: str) -> str:
    if is_untitled_uri(uri):
        return format_untitled_uri(uri)
    elif is_remote_uri(uri):
        return make_legacy_remote_path(uri_to_target_path(uri))
    elif is_local_uri(uri):
        return uri_to_target_path(uri)
    else:
        raise ValueError(f"Unexpected uri: {uri}")


def local_path_to_uri(path: str) -> str:
    if path.startswith("//"):
        # UNC
        return f"{FILE_URI_SCHEME}:{urllib.parse.quote(path)}"
    elif path[1:3] == ":\\":
        # Regular Windows path, needs special treatment on other platforms
        return pathlib.PureWindowsPath(path).as_uri()
    else:
        assert path.startswith("/")
        return f"{FILE_URI_SCHEME}://{urllib.parse.quote(path)}"


def remote_path_to_uri(path: str) -> str:
    assert path.startswith("/")
    return f"{REMOTE_URI_SCHEME}://netloc{urllib.parse.quote(path)}"


def is_untitled_uri(uri: str) -> bool:
    return uri.startswith(UNTITLED_URI_SCHEME + ":")


def is_local_uri(uri: str) -> bool:
    """Whether the file is "local" in the sense that it can be read and written with
    simple open-call. Includes UNC files in Windows (???)"""
    return uri.startswith(FILE_URI_SCHEME + ":")


def is_remote_uri(uri: str) -> bool:
    return uri.startswith(REMOTE_URI_SCHEME + ":")


def is_editor_supported_uri(uri: str) -> bool:
    return is_local_uri(uri) or is_remote_uri(uri) or is_untitled_uri(uri)


def format_untitled_uri(uri: str) -> str:
    return tr("<untitled>")


def make_legacy_remote_path(target_path):
    return get_runner().get_node_label() + REMOTE_PATH_MARKER + target_path


def is_local_project_dir(path: str) -> bool:
    if not os.path.isdir(path):
        return False

    for marker in PROJECT_MARKERS:
        if os.path.exists(os.path.join(path, marker)):
            return True

    return False


def is_local_venv_dir(path: str) -> bool:
    if not os.path.isdir(path):
        return False

    return os.path.isfile(os.path.join(path, "pyvenv.cfg"))


def get_project_venv_interpreters(project_path: str) -> List[str]:
    if not os.path.isdir(project_path):
        return []

    # TODO: try find Pyenv, Pipenv and Poetry interpreters

    name_ranking = [".venv", "venv", ".env"]

    exe_candidates = []
    for name in os.listdir(project_path):
        venv_candidate = os.path.join(project_path, name)
        if ("venv" in name or ".env" in name) and is_local_venv_dir(venv_candidate):
            if os.name == "nt":
                exe_candidate = os.path.join(venv_candidate, "Scripts", "python.exe")
            else:
                exe_candidate = os.path.join(venv_candidate, "bin", "python")

            if os.path.isfile(exe_candidate):
                if name in name_ranking:
                    rank = name_ranking.index(name)
                else:
                    rank = 10
                exe_candidates.append((rank, exe_candidate))

    return [candidate for _, candidate in sorted(exe_candidates)]
