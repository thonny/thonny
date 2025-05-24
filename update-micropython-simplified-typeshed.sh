#!/usr/bin/env bash

rm -rf thonny/vendored_libs/micropython-simplified-typeshed
pip install --no-user --target thonny/vendored_libs/micropython-simplified-typeshed micropython-microbit-stubs-en
