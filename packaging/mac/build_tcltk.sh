#!/usr/bin/env bash

TCLTK_VERSION=8.6.4

# COMPILE AND INSTALL AS FRAMEWORK
# (Seems that Tkinter won't be built, if I don't install it as framework)
############################################################
# wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl$TCLTK_VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tcl$TCLTK_VERSION-src.tar.gz

tar -xzf tcl$TCLTK_VERSION-src.tar.gz
cd tcl$TCLTK_VERSION/macosx
./configure --enable-framework
make 
sudo make install NATIVE_TCLSH=$PREFIX/bin/tclsh8.6
sudo chown -R $REGULAR_USER $PREFIX
sudo chown -R $REGULAR_USER $TEMP_BUILD_DIR
cd ../..

############################################################
#wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk$TCLTK_VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tk$TCLTK_VERSION-src.tar.gz

tar -xzf tk$TCLTK_VERSION-src.tar.gz
cd tk$TCLTK_VERSION/macosx
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --enable-framework --enable-aqua --disable-xss 
make 
sudo make install
sudo chown -R $REGULAR_USER $PREFIX
sudo chown -R $REGULAR_USER $TEMP_BUILD_DIR
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

chmod -R u+w $PREFIX

install_name_tool -id \
	$RELATIVE_LIBDIR/Tcl \
    $PREFIX/lib/Tcl 

install_name_tool -id \
	$RELATIVE_LIBDIR/Tk \
    $PREFIX/lib/Tk 
 
# DELETE FRAMEWORKS #############################################################
sudo rm -rf /Library/Frameworks/Tcl.framework/Versions/8.6/
sudo rm -rf /Library/Frameworks/Tk.framework/Versions/8.6/

