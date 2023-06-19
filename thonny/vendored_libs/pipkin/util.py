import os.path
import re
import subprocess
import sys
from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional, Set, Tuple

import pkg_resources

logger = getLogger(__name__)


@dataclass
class ParsedWheelFilename:
    project: str
    version: str
    build: Optional[str]
    python_tags: list[str]
    abi_tags: list[str]
    platform_tags: list[str]


def parse_wheel_filename(filename: str) -> ParsedWheelFilename:
    # Adapted from https://github.com/jwodder/wheel-filename/blob/1568eb2f1726425588550067f09f5c0fde6c9652/src/wheel_filename/__init__.py
    PYTHON_TAG_RGX = r"[\w\d]+"
    ABI_TAG_RGX = r"[\w\d]+"
    PLATFORM_TAG_RGX = r"[\w\d]+"

    WHEEL_FILENAME_CRGX = re.compile(
        r"(?P<project>[A-Za-z0-9](?:[A-Za-z0-9._]*[A-Za-z0-9])?)"
        r"-(?P<version>[A-Za-z0-9_.!+]+)"
        r"(?:-(?P<build>[0-9][\w\d.]*))?"
        r"-(?P<python_tags>{0}(?:\.{0})*)"
        r"-(?P<abi_tags>{1}(?:\.{1})*)"
        r"-(?P<platform_tags>{2}(?:\.{2})*)"
        r"\.[Ww][Hh][Ll]".format(PYTHON_TAG_RGX, ABI_TAG_RGX, PLATFORM_TAG_RGX)
    )
    basename = os.path.basename(os.fsdecode(filename))
    m = WHEEL_FILENAME_CRGX.fullmatch(basename)
    if not m:
        raise ValueError(f"Unexpected wheel filename {basename}")

    return ParsedWheelFilename(
        project=m.group("project"),
        version=m.group("version"),
        build=m.group("build"),
        python_tags=m.group("python_tags").split("."),
        abi_tags=m.group("abi_tags").split("."),
        platform_tags=m.group("platform_tags").split("."),
    )


def create_dist_info_version_name(dist_name: str, version: str) -> str:
    # https://packaging.python.org/en/latest/specifications/binary-distribution-format/#escaping-and-unicode
    # https://peps.python.org/pep-0440/
    safe_name = pkg_resources.safe_name(dist_name).replace("-", "_")
    safe_version = pkg_resources.safe_version(version)
    return f"{safe_name}-{safe_version}"


def get_windows_folder(ID: int) -> str:
    # http://stackoverflow.com/a/3859336/261181
    # http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
    if sys.platform == "win32":
        import ctypes.wintypes

        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, ID, 0, SHGFP_TYPE_CURRENT, buf)
        assert buf.value
        return buf.value
    else:
        raise AssertionError("Meant to be used only on Windows")


def get_windows_roaming_appdata_dir() -> str:
    return get_windows_folder(26)


def get_windows_local_appdata_dir() -> str:
    return get_windows_folder(28)


def get_user_cache_dir() -> str:
    if sys.platform == "win32":
        return os.path.join(get_windows_local_appdata_dir())
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches")
    else:
        return os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))


def get_base_executable():
    if sys.exec_prefix == sys.base_exec_prefix:
        return sys.executable

    if sys.platform == "win32":
        guess = sys.base_exec_prefix + "\\" + os.path.basename(sys.executable)
        if os.path.isfile(guess):
            return guess

    if os.path.islink(sys.executable):
        return os.path.realpath(sys.executable)

    raise RuntimeError("Don't know how to locate base executable")


def get_venv_executable(path: str) -> str:
    if sys.platform == "win32":
        return os.path.join(path, "Scripts", "python.exe")
    else:
        return os.path.join(path, "bin", "python3")


def get_venv_site_packages_path(venv_path: str) -> str:
    logger.debug("Querying site packages path for %s", venv_path)
    args = [
        get_venv_executable(venv_path),
        "-c",
        "import site; print([p for p in site.getsitepackages() if 'site-packages' in p][0])",
    ]
    result = subprocess.check_output(
        args,
        executable=args[0],
        text=True,
        stdin=subprocess.DEVNULL,
    ).strip()
    assert result.startswith(venv_path) and result != venv_path
    logger.debug("Got site packages path %s", result)
    return result


def parse_meta_dir_name(name: str) -> Tuple[str, str]:
    assert name.endswith(".dist-info")
    name, version = name[: -len(".dist-info")].split("-")
    return name, version


def parse_dist_file_name(file_name: str) -> Tuple[str, str, str]:
    file_name = file_name.lower()

    if file_name.endswith(".whl"):
        pwf = parse_wheel_filename(file_name)
        return pwf.project, pwf.version, ".whl"

    for suffix in [".zip", ".tar.gz"]:
        if file_name.endswith(suffix):
            file_name = file_name[: -len(suffix)]
            break
    else:
        raise AssertionError("Unexpected file name " + file_name)

    # dist name and version is separated by the dash, but both parts can also contain dashes...
    if file_name.count("-") == 1:
        dist_name, version = file_name.split("-")
    else:
        # assuming dashes in the version part have digit on their left and letter on their right
        # let's get rid of these
        tweaked_file_name = re.sub(r"(\d)-([a-zA-Z])", r"\1_\2", file_name)
        # now let's treat the rightmost dash as separator
        dist_name = tweaked_file_name.rsplit("-", maxsplit=1)[0]
        version = file_name[len(dist_name) + 1 :]

    return dist_name, version, suffix


def starts_with_continuation_byte(data: bytes) -> bool:
    return len(data) > 0 and is_continuation_byte(data[0])


def is_continuation_byte(byte: int) -> bool:
    return (byte & 0b11000000) == 0b10000000


def custom_normalize_dist_name(name: str) -> str:
    # https://peps.python.org/pep-0503/#normalized-names
    return pkg_resources.safe_name(name).lower().replace("-", "_").replace(".", "_")


def list_volumes(skip_letters: Optional[Set[str]] = None) -> List[str]:
    skip_letters = skip_letters or set()

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
    else:
        # 'posix' means we're on Linux or OSX (Mac).
        # Call the unix "mount" command to list the mounted volumes.
        mount_output = subprocess.check_output(["mount"], stdin=subprocess.DEVNULL).splitlines()
        return [x.split()[2].decode("utf-8") for x in mount_output]
