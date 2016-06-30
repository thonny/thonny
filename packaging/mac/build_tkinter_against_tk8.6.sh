#!/usr/bin/env bash

PYTHON_VERSION=3.5.2
RELEASE_NAME=Python-${PYTHON_VERSION}

curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/$RELEASE_NAME.tgz
tar xf $RELEASE_NAME.tgz
cd $RELEASE_NAME

# Take from env
# PREFIX=$HOME/thonny_template_build

TCLI=/Library/Frameworks/Tcl.framework/Versions/8.6/Headers
TCLL=/Library/Frameworks/Tcl.framework/Versions/8.6
TKI=/Library/Frameworks/Tk.framework/Versions/8.6/Headers
TKL=/Library/Frameworks/Tk.framework/Versions/8.6

./configure --prefix=$PREFIX LDFLAGS="-L$PREFIX/lib" CPPFLAGS="-I$PREFIX/include" \
	--with-tcltk-includes="-I$TCLI -I$TKI" \
	--with-tcltk-libs="-I$TCLL -I$TKL"

# NB! If you update xcode then first do:
# sudo xcodebuild -license

make
make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
#$PREFIX/bin/python3.5 -m idlelib


