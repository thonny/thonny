#!/usr/bin/env bash

if [ "$1" == "8.6" ]
then
	TCLTK_LONG_VERSION=8.6.4
	TCLTK_SHORT_VERSION=8.6
else
	TCLTK_LONG_VERSION=8.5.19
	TCLTK_SHORT_VERSION=8.5
fi

# COMPILE AND INSTALL AS FRAMEWORK
# (Seems that Tkinter won't be built, if I don't install it as framework)
############################################################
# wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tcl$TCLTK_LONG_VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tcl$TCLTK_LONG_VERSION-src.tar.gz

tar -xzf tcl$TCLTK_LONG_VERSION-src.tar.gz
cd tcl$TCLTK_LONG_VERSION/macosx
./configure --enable-framework
make 
sudo make install NATIVE_TCLSH=$PREFIX/bin/tclsh$TCLTK_SHORT_VERSION
sudo chown -R $REGULAR_USER $PREFIX
sudo chown -R $REGULAR_USER $TEMP_BUILD_DIR
cd ../..

############################################################
#wget ftp://ftp.tcl.tk/pub/tcl/tcl8_6/tk$TCLTK_LONG_VERSION-src.tar.gz
wget http://prdownloads.sourceforge.net/tcl/tk$TCLTK_LONG_VERSION-src.tar.gz

tar -xzf tk$TCLTK_LONG_VERSION-src.tar.gz
cd tk$TCLTK_LONG_VERSION/macosx
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --enable-framework --enable-aqua --disable-xss 
make 
sudo make install
sudo chown -R $REGULAR_USER $PREFIX
sudo chown -R $REGULAR_USER $TEMP_BUILD_DIR
cd ../..

# MAKE PRIVATE COPY FOR THONNY ########################################
mkdir -p $PREFIX/lib
mkdir -p $PREFIX/include
cp -f /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/Tcl $PREFIX/lib
cp -f /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/Tk $PREFIX/lib

cp -R /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/Resources/tcl8 $PREFIX/lib

mkdir $PREFIX/lib/tcl$TCLTK_SHORT_VERSION
mkdir $PREFIX/lib/tk$TCLTK_SHORT_VERSION
cp -R /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/Resources/Scripts/ $PREFIX/lib/tcl$TCLTK_SHORT_VERSION
cp -R /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/Resources/Scripts/ $PREFIX/lib/tk$TCLTK_SHORT_VERSION


# Following are needed for building Tcl/Tk extensions (eg. TkHtml)
cp -f /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/tclconfig.sh $PREFIX/lib
#cp -f /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/pkgconfig $PREFIX/lib
cp -f /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/libtclstub$TCLTK_SHORT_VERSION.a $PREFIX/lib
cp -rf /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/PrivateHeaders/* $PREFIX/include
cp -rf /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION/Headers/* $PREFIX/include

cp -f /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/tkConfig.sh $PREFIX/lib
#cp -f /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/pkgconfig $PREFIX/lib
cp -f /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/libtkstub$TCLTK_SHORT_VERSION.a $PREFIX/lib
cp -rf /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/PrivateHeaders/* $PREFIX/include
cp -rf /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION/Headers/* $PREFIX/include



# UPDATE LINKS #############################################################################

chmod -R u+w $PREFIX

install_name_tool -id \
	$RELATIVE_LIBDIR/Tcl \
    $PREFIX/lib/Tcl 

install_name_tool -id \
	$RELATIVE_LIBDIR/Tk \
    $PREFIX/lib/Tk 
 
# DELETE FRAMEWORKS #############################################################
#sudo rm -rf /Library/Frameworks/Tcl.framework/Versions/$TCLTK_SHORT_VERSION
#sudo rm -rf /Library/Frameworks/Tk.framework/Versions/$TCLTK_SHORT_VERSION

