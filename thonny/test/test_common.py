import builtins
import os

import thonny.common
from thonny.common import path_startswith, try_get_base_executable


def test_path_startswith():
    assert path_startswith("/kala/pala", "/kala")
    assert path_startswith("/kala/pala", "/kala/")

    assert not path_startswith("/kala/pala", "/pala")
    assert not path_startswith("/kalapala/pala", "/kala")

    if os.name == "nt":
        assert path_startswith("/kala/pala", "/KALA")
    else:
        assert not path_startswith("/kala/pala", "/KALA")

    if os.name == "nt":
        assert path_startswith("C:\\foo\\bar", "C:\\foo")
        assert path_startswith("C:\\foo", "C:\\")
        assert path_startswith("C:/foo", "C:\\")
        assert path_startswith("C:\\foo", "C:/")

        assert path_startswith("C:\\foo\\dir\\file", "C:\\foo")
        assert path_startswith("C:/foo\\dir\\file", "c:\\FOO")
        assert path_startswith("c:\\FOO\\dir\\file", "C:/foo")

        assert path_startswith("C:\\FOO\\dir\\dir2\\..\\ee", "C:/foo/dir/ee")

        assert path_startswith("c:\\foo\\bar.txt/kala\\pala", "C:\\foo\\bar.txt/kala")
        assert path_startswith("c:\\foo\\bar.txt/kala\\pala", "C:\\")

        assert not path_startswith("C:\\kalapala\\pala", "C:\\kala")


def test_try_get_base_executable_reads_pyvenv_cfg_as_utf8(tmp_path, monkeypatch):
    # venv writes pyvenv.cfg as UTF-8; simulate a non-UTF-8 locale (e.g. Windows)
    def open_with_legacy_locale(*args, **kwargs):
        kwargs.setdefault("encoding", "cp1252")
        return builtins.open(*args, **kwargs)

    monkeypatch.setattr(thonny.common, "open", open_with_legacy_locale, raising=False)

    base_exe = os.path.join("Users", "Łukasz ✨", "Python312", "python.exe")
    venv_dir = tmp_path / "venv"
    (venv_dir / "Scripts").mkdir(parents=True)
    cfg_text = f"home = {os.path.dirname(base_exe)}\nexecutable = {base_exe}\n"
    (venv_dir / "pyvenv.cfg").write_text(cfg_text, encoding="utf-8")

    assert try_get_base_executable(str(venv_dir / "Scripts" / "python.exe")) == base_exe
