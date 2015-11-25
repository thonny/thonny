#!/usr/bin/env bash

# COMPILE PYTHON ###############################################

PYTHON_VERSION=3.5.1
RELEASE_NAME=Python-${PYTHON_VERSION}rc1

wget https://www.python.org/ftp/python/$PYTHON_VERSION/$RELEASE_NAME.tar.xz
tar xf $RELEASE_NAME.tar.xz
cd $RELEASE_NAME

# set LD_LIBRARY_PATH (https://mail.python.org/pipermail/tkinter-discuss/2011-March/002808.html)
export LD_LIBRARY_PATH=$PREFIX/lib

# compile and install Python
./configure \
	--prefix=$PREFIX \
	--with-tcltk-includes=-I$PREFIX/include \
	--with-tcltk-libs=-L$PREFIX/lib

make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
#$PREFIX/bin/python3.5 -m idlelib

# CLEAN PYTHON ###########################################
rm -rf $PREFIX/share
# rm -rf $PREFIX/include # TODO: pyconfig.h is required by pip
rm -rf $PREFIX/man
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

