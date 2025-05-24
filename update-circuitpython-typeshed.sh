#!/usr/bin/env bash

rm -rf thonny/vendored_libs/circuitpython-typeshed
pip install --no-user --target thonny/vendored_libs/circuitpython-typeshed circuitpython-typeshed
