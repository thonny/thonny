#!/usr/bin/env bash

PYTHON_VERSION=3.5.1
RELEASE_NAME=Python-${PYTHON_VERSION}

curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/$RELEASE_NAME.tgz
tar xf $RELEASE_NAME.tgz
cd $RELEASE_NAME

# compile and install Python
./configure --prefix=$PREFIX LDFLAGS="-L$PREFIX/lib" CPPFLAGS="-I$PREFIX/include"

make
make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
#$PREFIX/bin/python3.5 -m idlelib


$PREFIX/bin/python3.5 -m pip install jedi

