#!/usr/bin/env bash


rm -rf $PREFIX/share
rm -rf $PREFIX/man
# rm -rf $PREFIX/include # may be required by pip

rm $PREFIX/bin/2to3-3.5
rm $PREFIX/bin/easy_install-3.5
rm $PREFIX/bin/idle3.5
rm $PREFIX/bin/pip3.5
rm $PREFIX/bin/pydoc3.5
rm $PREFIX/bin/python3.5m
rm $PREFIX/bin/python3.5m-config
rm $PREFIX/bin/pyvenv-3.5
rm $PREFIX/bin/tclsh8.6
rm $PREFIX/bin/wish8.6

rm -f $PREFIX/lib/libpython3.5m.a

rm -rf $PREFIX/lib/python3.5/__pycache__
# rm -rf $PREFIX/lib/python3.5/config-3.5m # TODO: makefile is required
rm -rf $PREFIX/lib/python3.5/test

find $PREFIX/lib -name '*.pyc' -delete
find $PREFIX/lib -name '*.exe' -delete