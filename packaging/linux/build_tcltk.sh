#!/usr/bin/env bash

set -e

VERSION=8.6.12

# COMPILE TCL/TK ####################################################
wget https://downloads.sourceforge.net/project/tcl/Tcl/${VERSION}/tcl${VERSION}-src.tar.gz
#wget https://deac-riga.dl.sourceforge.net/project/tcl/Tcl/${VERSION}/tcl${VERSION}-src.tar.gz
# wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl$VERSION-src.tar.gz
tar -xzf tcl${VERSION}-src.tar.gz
cd tcl${VERSION}/unix
./configure --prefix=$PREFIX
make install
cd ../..

wget https://downloads.sourceforge.net/project/tcl/Tcl/${VERSION}/tk${VERSION}-src.tar.gz
#wget https://deac-riga.dl.sourceforge.net/project/tcl/Tcl/${VERSION}/tk${VERSION}-src.tar.gz
# wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk$VERSION-src.tar.gz
tar -xzf tk$VERSION-src.tar.gz
cd tk${VERSION}/unix
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --prefix=$PREFIX --disable-xss
make install
cd ../..
