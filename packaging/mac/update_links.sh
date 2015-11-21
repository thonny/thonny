#!/usr/bin/env bash

chmod u+w $PREFIX/lib/*.dylib


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
# ID
install_name_tool -id \
	$RELATIVE_LIBDIR/libcrypto.1.0.0.dylib \
    $PREFIX/lib/libcrypto.1.0.0.dylib 

install_name_tool -id \
	$RELATIVE_LIBDIR/libssl.1.0.0.dylib \
    $PREFIX/lib/libssl.1.0.0.dylib 

# _ssl
install_name_tool -change \
    $PREFIX/lib/libssl.1.0.0.dylib \
	$RELATIVE_LIBDIR/libssl.1.0.0.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_ssl.cpython-35m-darwin.so 

install_name_tool -change \
    $PREFIX/lib/libcrypto.1.0.0.dylib \
	$RELATIVE_LIBDIR/libcrypto.1.0.0.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_ssl.cpython-35m-darwin.so 

# _hashlib

install_name_tool -change \
    $PREFIX/lib/libssl.1.0.0.dylib \
	$RELATIVE_LIBDIR/libssl.1.0.0.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_hashlib.cpython-35m-darwin.so 

install_name_tool -change \
    $PREFIX/lib/libcrypto.1.0.0.dylib \
	$RELATIVE_LIBDIR/libcrypto.1.0.0.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_hashlib.cpython-35m-darwin.so 


# _lzma #################################
install_name_tool -id \
	$RELATIVE_LIBDIR/liblzma.5.dylib \
    $PREFIX/lib/liblzma.5.dylib 



install_name_tool -change \
    $PREFIX/lib/liblzma.5.dylib \
	$RELATIVE_LIBDIR/liblzma.5.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_lzma.cpython-35m-darwin.so 

