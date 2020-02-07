#!/usr/bin/env python3

import sys
import os.path

target_dir = sys.argv[1]
script_dir = os.path.abspath(os.path.dirname(__file__))
old_prelude1=b"#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3"
old_prelude2=b"#!" + script_dir.encode("ASCII") + b"/build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3"

# https://stackoverflow.com/a/33225909/261181
new_prelude=b"""#!/bin/sh
"exec" "`dirname $0`/python3.7" "$0" "$@"

"""

for name in os.listdir(target_dir):
    full_path = os.path.join(target_dir, name)
    if os.path.isfile(full_path) and not os.path.islink(full_path):
        with open(full_path, mode="br") as f:
            first_line = f.readline()
            if first_line.startswith(old_prelude1) or first_line.startswith(old_prelude2):
                new_content = new_prelude + f.read()
            else:
                new_content = None
        
        if new_content is not None:
            with open(full_path, mode="bw") as f:
                f.write(new_content)
                