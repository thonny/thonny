#!/usr/bin/env bash

PYTHON_VERISION=3.5.0

curl -O https://www.python.org/ftp/python/$PYTHON_VERISION/Python-$PYTHON_VERISION.tgz
tar xf Python-$PYTHON_VERISION.tgz
cd Python-$PYTHON_VERISION

# compile and install Python
./configure --prefix=$PREFIX LDFLAGS="-L$PREFIX/lib" CPPFLAGS="-I$PREFIX/include"

make
make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
#$PREFIX/bin/python3.5 -m idlelib




