#!/usr/bin/env bash

# This should be run before creating the framework template

INITIAL_DIR=$(pwd)
TEMP_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/temp_build_dir
VERSION=8.6.5

# https://github.com/tcltk/tcl/tree/master/macosx
export MACOSX_DEPLOYMENT_TARGET=10.6
export CFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6"
export LDFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6"

rm -rf $TEMP_DIR/build
rm -rf $TEMP_DIR/tcl$VERSION
rm -rf $TEMP_DIR/tk$VERSION

# COMPILE AND INSTALL AS FRAMEWORKS
# Tcl ###########################################################
cd $TEMP_DIR
# wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl$VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tcl$VERSION-src.tar.gz

tar -xzf tcl$VERSION-src.tar.gz
cd tcl$VERSION/macosx
./configure --enable-framework
make 
sudo make install 
cd $INITIAL_DIR

# Tk ###########################################################
cd $TEMP_DIR
#wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk$VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tk$VERSION-src.tar.gz

tar -xzf tk$VERSION-src.tar.gz
cd tk$VERSION/macosx
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --enable-framework --enable-aqua --disable-xss 
make 
sudo make install
cd $INITIAL_DIR
	