#!/usr/bin/env python3

import sys
import os.path

typeshed_path = "/path/to/typeshed"

requests_responses = {
    'import os, os.path, sys; normalize = lambda p: os.path.normcase(os.path.normpath(p)); cwd = normalize(os.getcwd()); orig_sys_path = [p for p in sys.path if p != ""]; sys.path[:] = [p for p in sys.path if p != "" and normalize(p) != cwd]; import sys, json; json.dump(dict(path=orig_sys_path, prefix=sys.prefix), sys.stdout)'
    : f'{"path": ["{typeshed_path}"], "prefix": "{typeshed_path}"}',
    'import os, os.path, sys; normalize = lambda p: os.path.normcase(os.path.normpath(p)); cwd = normalize(os.getcwd()); orig_sys_path = [p for p in sys.path if p != ""]; sys.path[:] = [p for p in sys.path if p != "" and normalize(p) != cwd]; import sys, json; json.dump(tuple(sys.version_info), sys.stdout)'
    : '[3, 8, 0, "final", 0]',
}

with open(os.path.expanduser("~/Desktop/fakepython.log"), "at", encoding="utf-8") as fp:
    fp.write("Responding to:\n")
    fp.write(os.getcwd() + "\n")
    fp.write(str(sys.argv) + "\n")


code = sys.argv[-1]
response = requests_responses.get(code)
if response is not None:
    print(response, end="")
else:
    print("UNKNOWN QUERY")
    exit(1)

