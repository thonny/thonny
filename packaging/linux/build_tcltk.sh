#!/usr/bin/env bash

set -e

# COMPILE TCL/TK ####################################################
# wget http://prdownloads.sourceforge.net/tcl/tcl8.6.5-src.tar.gz
wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl8.6.5-src.tar.gz
tar -xzf tcl8.6.5-src.tar.gz
cd tcl8.6.5/unix
./configure --prefix=$PREFIX
make install
cd ../..

# wget http://prdownloads.sourceforge.net/tcl/tk8.6.5-src.tar.gz
wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk8.6.5-src.tar.gz
tar -xzf tk8.6.5-src.tar.gz
cd tk8.6.5/unix
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --prefix=$PREFIX --disable-xss 
make install
cd ../..
