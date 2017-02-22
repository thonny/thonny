#!/usr/bin/env bash

# TODO: produced tkinter doesn't work in 10.6

# Official tkinter is compiled against Tk 8.5, I want 8.6 #################################
# Let's compile one against 8.6
# (I tried compiling just Python against framework tcl/tk but for some reason it didn't work
# so here I compile everything (tcl, tk, python) just to get _tkinter....so

PREFIX=$HOME/pytcltk
rm -rf $PREFIX
mkdir -p $PREFIX

INITIAL_DIR=$(pwd)
TEMP_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/temp_build_dir

rm -rf $TEMP_DIR/*

export MACOSX_DEPLOYMENT_TARGET=10.6
export CFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -I$PREFIX/include"
export LDFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -L$PREFIX/lib"
export CXXFLAGS="$CFLAGS"
export ARCHFLAGS="-arch i386 -arch x86_64"

export DYLD_LIBRARY_PATH=$PREFIX/lib
echo "$PREFIX"

# tcl-tk
VERSION=8.6.5

# Tcl ###########################################################
cd $TEMP_DIR
# wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl$VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tcl$VERSION-src.tar.gz


tar -xzf tcl$VERSION-src.tar.gz

cd tcl$VERSION/unix
./configure --prefix=$PREFIX
make 
make install 
cd $INITIAL_DIR


# Tk ###########################################################
cd $TEMP_DIR
#wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk$VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tk$VERSION-src.tar.gz

tar -xzf tk$VERSION-src.tar.gz
cd tk$VERSION/unix
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --prefix=$PREFIX --enable-aqua --disable-xss 
make 
make install
cd $INITIAL_DIR


# python -------------------------------------------------
PYTHON_VERSION=3.6.0
RELEASE_NAME=Python-${PYTHON_VERSION}

cd $TEMP_DIR
curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/$RELEASE_NAME.tgz
tar xf $RELEASE_NAME.tgz
cd $RELEASE_NAME

# https://github.com/python/cpython/tree/master/Mac

#./configure --prefix=$PREFIX \
./configure --prefix=$PREFIX --enable-universalsdk --with-universal-archs=intel \
	--with-tcltk-includes="-I$PREFIX/include" \
	--with-tcltk-libs="-L$PREFIX/lib -ltk8.6 -ltcl8.6" \

make
make altinstall # TODO: copy from build dir??
cd $INITIAL_DIR


# otool -L ~/pytcltk/lib/python3.6/lib-dynload/_tkinter.cpython-35m-darwin.so 

# Copy to framework template ###############################################################
# LOCAL_FRAMEWORKS=$HOME/thonny_template_build/Thonny.app/Contents/Frameworks

TKINTER_FILENAME=_tkinter.cpython-35m-darwin.so
LOCAL_TKINTER=$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/$TKINTER_FILENAME
TKINTER86=$PREFIX/lib/python3.6/lib-dynload/$TKINTER_FILENAME
cp -f $TKINTER86 $LOCAL_TKINTER

chmod u+w $LOCAL_TKINTER

# Update links ##############################################################################
install_name_tool -change \
    $PREFIX/lib/libtk8.6.dylib \
	@rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_TKINTER 

install_name_tool -change \
    $PREFIX/lib/libtcl8.6.dylib \
	@rpath/Tk.framework/Versions/8.6/Tk \
    $LOCAL_TKINTER 

