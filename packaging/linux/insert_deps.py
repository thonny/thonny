#!/usr/bin/env python3

import sys

source_path = sys.argv[1]
target_path = sys.argv[2]

replacement = ""
with open(source_path) as fp:
    for line in fp:
        dep = line.split("#")[0].strip()
        if dep:
            replacement += f"'{dep}' "

with open(target_path, encoding="utf-8") as fp:
    original_text = fp.read()

with open(target_path, "w", encoding="utf-8") as fp:
    fp.write(original_text.replace("_DEPS_", replacement))
