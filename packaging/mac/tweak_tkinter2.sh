#!/usr/bin/env bash

PREFIX=$HOME/pytcltk
rm -rf $PREFIX
mkdir -p $PREFIX

INITIAL_DIR=$(pwd)
TEMP_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/temp_build_dir

rm -rf $TEMP_DIR/*

#export MACOSX_DEPLOYMENT_TARGET=10.6
export CFLAGS="-arch i386 -arch x86_64 -I$PREFIX/include"
#export CFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -I$PREFIX/include"
#export CFLAGS="-I$PREFIX/include"
export LDFLAGS="-arch i386 -arch x86_64 -L$PREFIX/lib"
#export LDFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -L$PREFIX/lib"
#export LDFLAGS="-L$PREFIX/lib"
export CXXFLAGS="$CFLAGS"
#export CPPFLAGS="$CFLAGS"
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
PYTHON_VERSION=3.5.2
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


otool -L ~/pytcltk/lib/python3.5/lib-dynload/_tkinter.cpython-35m-darwin.so 