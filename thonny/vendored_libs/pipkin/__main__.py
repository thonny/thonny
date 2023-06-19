"""
MIT License

Copyright (c) 2023 Aivar Annamaa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
import subprocess
import sys
import textwrap
from typing import List, Optional

from pipkin import main

logger = logging.getLogger(__name__)

MP_ORG_INDEX = "https://micropython.org/pi"
PYPI_INDEX = "https://pypi.org/pypi"
PYPI_SIMPLE_INDEX = "https://pypi.org/simple"
DEFAULT_INDEX_URLS = [MP_ORG_INDEX, PYPI_INDEX]
SERVER_ENCODING = "utf-8"

__version__ = "0.2b1"

"""
steps:
    - infer target if no explicit connection parameters are given
    - connect (MP)
    - determine target location on the device/mount
    - sync RTC (MP, install, uninstall). Not required for CP?
    - ensure temp venv for pip operations
    - fetch METADATA-s and RECORD-s (may be empty in all cases except "show -f") and populate venv
    - record current state
    - invoke pip (translate paths in the output)
    - determine deleted and changed dists and remove these on the target (according to actual RECORD-s)
    - determine new and changed dists and copy these to the target
    - clear venv



"""


sys.exit(main(sys.argv[1:]))
