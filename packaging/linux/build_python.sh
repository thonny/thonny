#!/usr/bin/env bash

set -e

# COMPILE PYTHON ###############################################

PYTHON_VERSION=3.7.9
RELEASE_NAME=Python-${PYTHON_VERSION}

wget https://www.python.org/ftp/python/$PYTHON_VERSION/$RELEASE_NAME.tar.xz
tar xf $RELEASE_NAME.tar.xz
cd $RELEASE_NAME

# set LD_LIBRARY_PATH (https://mail.python.org/pipermail/tkinter-discuss/2011-March/002808.html)
export LD_LIBRARY_PATH=$PREFIX/lib
export LDFLAGS="-L$PREFIX/lib"
export CPPFLAGS="-I$PREFIX/include"

# compile and install Python
./configure \
	--prefix=$PREFIX \
	--with-tcltk-includes=-I$PREFIX/include \
	--with-tcltk-libs=-L$PREFIX/lib

make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
#$PREFIX/bin/python3.7 -m idlelib

