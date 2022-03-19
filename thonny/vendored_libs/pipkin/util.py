import os.path
import subprocess
import sys
from typing import Tuple


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
    result = subprocess.check_output(
        [get_venv_executable(venv_path), "-c", "import site; print(site.getsitepackages()[0])"],
        text=True,
    ).strip()
    assert result.startswith(venv_path)
    return result


def parse_meta_dir_name(name: str) -> Tuple[str, str]:
    assert name.endswith(".dist-info")
    name, version = name[: -len(".dist-info")].split("-")
    return name, version


def starts_with_continuation_byte(data: bytes) -> bool:
    return len(data) > 0 and is_continuation_byte(data[0])


def is_continuation_byte(byte: int) -> bool:
    return (byte & 0b11000000) == 0b10000000
