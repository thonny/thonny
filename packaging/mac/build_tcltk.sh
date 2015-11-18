#!/usr/bin/env bash

# COMPILE AND INSTALL AS FRAMEWORK ###########################################################
wget http://prdownloads.sourceforge.net/tcl/tcl8.6.4-src.tar.gz
tar -xzf tcl8.6.4-src.tar.gz
cd tcl8.6.4/macosx
./configure --enable-framework
make 
sudo make install
cd ../..

wget http://prdownloads.sourceforge.net/tcl/tk8.6.4-src.tar.gz
tar -xzf tk8.6.4-src.tar.gz
cd tk8.6.4/macosx
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --enable-framework --enable-aqua --disable-xss 
make 
sudo make install
cd ../..

# MAKE PRIVATE COPY FOR THONNY ########################################
mkdir -p $PREFIX/lib
cp -f /Library/Frameworks/Tcl.framework/Versions/8.6/Tcl $PREFIX/lib
cp -f /Library/Frameworks/Tk.framework/Versions/8.6/Tk $PREFIX/lib
cp -R /Library/Frameworks/Tcl.framework/Versions/8.6/Resources/tcl8 $PREFIX/lib

mkdir $PREFIX/lib/tcl8.6
mkdir $PREFIX/lib/tk8.6
cp -R /Library/Frameworks/Tcl.framework/Versions/8.6/Resources/Scripts/ $PREFIX/lib/tcl8.6
cp -R /Library/Frameworks/Tk.framework/Versions/8.6/Resources/Scripts/ $PREFIX/lib/tk8.6

# UPDATE LINKS #############################################################################

chmod 655 $PREFIX/lib/Tcl
chmod 655 $PREFIX/lib/Tk

install_name_tool -id \
	$RELATIVE_LIBDIR/Tcl \
    $PREFIX/lib/Tcl 


install_name_tool -id \
	$RELATIVE_LIBDIR/Tk \
    $PREFIX/lib/Tk 
 
chmod 555 $PREFIX/lib/Tcl
chmod 555 $PREFIX/lib/Tk


