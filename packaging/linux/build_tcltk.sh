#!/usr/bin/env bash

set -e

# COMPILE TCL/TK ####################################################
# wget http://prdownloads.sourceforge.net/tcl/tcl8.6.8-src.tar.gz
VERSION=8.6.10
wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl$VERSION-src.tar.gz
tar -xzf tcl$VERSION-src.tar.gz
cd tcl$VERSION/unix
./configure --prefix=$PREFIX
make install
cd ../..

# wget http://prdownloads.sourceforge.net/tcl/tk8.6.8-src.tar.gz
wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk$VERSION-src.tar.gz
tar -xzf tk$VERSION-src.tar.gz
cd tk$VERSION/unix
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --prefix=$PREFIX --disable-xss 
make install
cd ../..
