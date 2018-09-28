import os

from thonny.common import path_startswith


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
