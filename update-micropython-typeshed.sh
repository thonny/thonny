#!/usr/bin/env bash

rm -rf thonny/vendored_libs/micropython-typeshed
pip install --no-user --target thonny/vendored_libs/micropython-typeshed micropython-typeshed
