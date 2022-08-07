#!/bin/bash

TMPDIR=$(mktemp -d -p .)
tar -zxf dist/thonny-4.0.0b3-dev-x86_64.tar.gz -C $TMPDIR
$TMPDIR/thonny/install
rm -rf $TMPDIR
