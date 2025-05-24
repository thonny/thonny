#!/usr/bin/env bash

rm -rf thonny/vendored_libs/micropython-unix-typeshed
pip install --no-user --target thonny/vendored_libs/micropython-unix-typeshed micropython-unix-stubs
