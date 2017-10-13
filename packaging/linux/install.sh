#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# http://stackoverflow.com/a/677212/261181
if hash python3 2>/dev/null; then
    python3 "$THIS_DIR"/install.py "$@"
else
    python "$THIS_DIR"/install.py "$@"
fi
