import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from thonny.ui_utils import _ZenityDialogProvider


@pytest.mark.parametrize("filename", ["example.py", "example.py ", "example.py\t", "example.py\n"])
@pytest.mark.skipif(os.name == "nt", reason="These filenames require a POSIX filesystem")
def test_zenity_preserves_filename_whitespace(tmp_path, filename):
    path = tmp_path / filename
    path.write_text("print('hello')\n")
    result = subprocess.CompletedProcess(["zenity"], 0, stdout=str(path) + "\n", stderr="")

    with (
        patch("thonny.ui_utils.subprocess.run", return_value=result),
        patch.object(_ZenityDialogProvider, "_check_zenity_exists", return_value=True),
    ):
        selected_paths = [
            _ZenityDialogProvider.askopenfilename(parent=None),
            _ZenityDialogProvider.asksaveasfilename(parent=None),
        ]

    for selected_path in selected_paths:
        assert selected_path == str(path)
        assert Path(selected_path).read_text() == "print('hello')\n"


def test_zenity_cancellation():
    result = subprocess.CompletedProcess(["zenity"], 1, stdout="", stderr="")

    with patch("thonny.ui_utils.subprocess.run", return_value=result):
        assert _ZenityDialogProvider._call(["--file-selection"]) is None
