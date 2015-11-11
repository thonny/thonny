PREFIX=/opt/pythonny

# COMPILE TCL/TK ####################################################################################
# TODO




# COMPILE LIBRARIES REQUIRED BY PYTHON ##############################################################
# TODO


# COMPILE PYTHON ####################################################################################
# TODO


# UPDATE LINKS ######################################################################################
RELATIVE_LIBDIR=@executable_path/../lib

# Tcl/Tk #############################
cp -f /Library/Frameworks/Tcl.framework/Versions/8.6/Tcl $PREFIX/lib
cp -f /Library/Frameworks/Tk.framework/Versions/8.6/Tk $PREFIX/lib
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

mkdir $PREFIX/lib/tcl8.6
mkdir $PREFIX/lib/tk8.6
cp -R /Library/Frameworks/Tcl.framework/Versions/8.6/Resources/tcl8 $PREFIX/lib
cp -R /Library/Frameworks/Tcl.framework/Versions/8.6/Resources/Scripts/ $PREFIX/lib/tcl8.6
cp -R /Library/Frameworks/Tk.framework/Versions/8.6/Resources/Scripts/ $PREFIX/lib/tk8.6


# _tkinter ##########################
install_name_tool -change \
    /Library/Frameworks/Tcl.framework/Versions/8.6/Tcl \
	$RELATIVE_LIBDIR/Tcl \
    $PREFIX/lib/python3.5/lib-dynload/_tkinter.cpython-35m-darwin.so 

install_name_tool -change \
    /Library/Frameworks/Tk.framework/Versions/8.6/Tk \
	$RELATIVE_LIBDIR/Tk \
    $PREFIX/lib/python3.5/lib-dynload/_tkinter.cpython-35m-darwin.so 

# _ssl #################################
cp -f /usr/local/opt/openssl/lib/libssl.1.0.0.dylib $PREFIX/lib
cp -f /usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib $PREFIX/lib

chmod 655 $PREFIX/lib/libcrypto.1.0.0.dylib
chmod 655 $PREFIX/lib/libssl.1.0.0.dylib

install_name_tool -id \
	$RELATIVE_LIBDIR/libcrypto.1.0.0.dylib \
    $PREFIX/lib/libcrypto.1.0.0.dylib 

install_name_tool -id \
	$RELATIVE_LIBDIR/libssl.1.0.0.dylib \
    $PREFIX/lib/libssl.1.0.0.dylib 


install_name_tool -change \
    /usr/local/opt/openssl/lib/libssl.1.0.0.dylib \
	$RELATIVE_LIBDIR/libssl.1.0.0.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_ssl.cpython-35m-darwin.so 

install_name_tool -change \
    /usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib \
	$RELATIVE_LIBDIR/libcrypto.1.0.0.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_ssl.cpython-35m-darwin.so 

# _lzma #################################
install_name_tool -change \
    /usr/local/lib/liblzma.5.dylib \
	$RELATIVE_LIBDIR/liblzma.5.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_lzma.cpython-35m-darwin.so 



# CLEAN UP ######################################################################################
rm -rf $PREFIX/share
rm -rf $PREFIX/include
rm $PREFIX/bin/2to3-3.5
rm $PREFIX/bin/easy_install-3.5
rm $PREFIX/bin/idle3.5
rm $PREFIX/bin/pip3.5
rm $PREFIX/bin/pydoc3.5
rm $PREFIX/bin/python3.5m
rm $PREFIX/bin/python3.5m-config
rm $PREFIX/bin/pyvenv-3.5

rm $PREFIX/lib/libpython3.5m.a

rm -rf $PREFIX/lib/python3.5/__pycache__
rm -rf $PREFIX/lib/python3.5/config-3.5m # TODO: makefile is required
rm -rf $PREFIX/lib/python3.5/test

find $PREFIX/lib -name '*.pyc' -delete

    