#!/bin/bash

TMPDIR=$(mktemp -d -p .)
tar -zxf dist/thonny-4.0.0-dev-x86_64-alt.tar.gz -C $TMPDIR
$TMPDIR/thonny/install
rm -rf $TMPDIR
