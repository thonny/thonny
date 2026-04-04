#!/bin/bash
set -e
# https://github.com/lektor/lektor/blob/master/gui/bin/make-python-framework-relocatable

# Take from env
# LOCAL_FRAMEWORKS=$HOME/thonny_template_build_314/Thonny.app/Contents/Frameworks

VERSION=3.14
ORIGINAL_FRAMEWORK_PATH=/Library/Frameworks/Python.framework
NEW_FRAMEWORK_PATH=$LOCAL_FRAMEWORKS/Python.framework

rm -rf $NEW_FRAMEWORK_PATH
mkdir -p $NEW_FRAMEWORK_PATH/Versions/$VERSION

cp -R $ORIGINAL_FRAMEWORK_PATH/Versions/3.14 $NEW_FRAMEWORK_PATH/Versions/

BIN_EXE=$NEW_FRAMEWORK_PATH/Versions/$VERSION/bin/python$VERSION

# delete everything in bin except python3.14
#find $NEW_FRAMEWORK_PATH/Versions/$VERSION/bin -type f -maxdepth 1 ! -name python$VERSION -delete

# Make main binaries and libraries relocatable
BUNDLE_EXE=$NEW_FRAMEWORK_PATH/Versions/$VERSION/Resources/Python.app/Contents/MacOS/Python
ORIG_LIB=$ORIGINAL_FRAMEWORK_PATH/Versions/$VERSION/lib
COPIED_LIB=$NEW_FRAMEWORK_PATH/Versions/$VERSION/lib
RPATH_LIB=@rpath/Python.framework/Versions/$VERSION/lib

ORIG_MAIN_LIB=$ORIGINAL_FRAMEWORK_PATH/Versions/$VERSION/Python
NEW_MAIN_LIB=$NEW_FRAMEWORK_PATH/Versions/$VERSION/Python
MAIN_LIB_LOCAL_NAME=@rpath/Python.framework/Versions/$VERSION/Python

chmod u+w $NEW_MAIN_LIB $BIN_EXE $BUNDLE_EXE

install_name_tool -change $ORIG_MAIN_LIB $MAIN_LIB_LOCAL_NAME $BIN_EXE
install_name_tool -add_rpath @executable_path/../../../../ $BIN_EXE

install_name_tool -change $ORIG_MAIN_LIB $MAIN_LIB_LOCAL_NAME ${BIN_EXE}-intel64
install_name_tool -add_rpath @executable_path/../../../../ ${BIN_EXE}-intel64

install_name_tool -id @rpath/Python.framework/Versions/$VERSION/Python $NEW_MAIN_LIB


install_name_tool -change $ORIG_MAIN_LIB $MAIN_LIB_LOCAL_NAME $BUNDLE_EXE
install_name_tool -add_rpath @executable_path/../../../../../../../ $BUNDLE_EXE

# update tkinter links
chmod 0755 $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Tcl
install_name_tool -id \
    @rpath/Tcl.framework/Tcl \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Tcl

chmod 0755 $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tk.framework/Tk
install_name_tool -id \
    @rpath/Tk.framework/Tk \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tk.framework/Tk

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Tcl \
    @rpath/Tcl.framework/Tcl \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tk.framework/Tk

install_name_tool -add_rpath \
    @loader_path/../../../Frameworks \
    $COPIED_LIB/python3.14/lib-dynload/_tkinter.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Tcl \
    @rpath/Tcl.framework/Tcl \
    $COPIED_LIB/python3.14/lib-dynload/_tkinter.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/Frameworks/Tk.framework/Tk \
    @rpath/Tk.framework/Tk \
    $COPIED_LIB/python3.14/lib-dynload/_tkinter.cpython-314-darwin.so

echo "review tkinter"
otool -L "$LOCAL_FRAMEWORKS/Python.framework/Versions/$VERSION/lib/python$VERSION/lib-dynload/_tkinter.cpython-314-darwin.so"
otool -L "$LOCAL_FRAMEWORKS/Python.framework/Versions/$VERSION/Frameworks/Tk.framework/Tk"
otool -D "$LOCAL_FRAMEWORKS/Python.framework/Versions/$VERSION/Frameworks/Tcl.framework/Tcl"
otool -D "$LOCAL_FRAMEWORKS/Python.framework/Versions/$VERSION/Frameworks/Tk.framework/Tk"

# update libcrypto, libssl and hashlib links
install_name_tool \
    -id $RPATH_LIB/libcrypto.3.dylib \
    -change $ORIG_LIB/libcrypto.3.dylib $RPATH_LIB/libcrypto.3.dylib \
    $COPIED_LIB/libcrypto.3.dylib

install_name_tool \
    -id $RPATH_LIB/libssl.3.dylib \
    -change $ORIG_LIB/libssl.3.dylib $RPATH_LIB/libssl.3.dylib \
    -change $ORIG_LIB/libcrypto.3.dylib $RPATH_LIB/libcrypto.3.dylib \
    $COPIED_LIB/libssl.3.dylib

install_name_tool \
    -change $ORIG_LIB/libssl.3.dylib $RPATH_LIB/libssl.3.dylib \
    -change $ORIG_LIB/libcrypto.3.dylib $RPATH_LIB/libcrypto.3.dylib \
    $COPIED_LIB/python3.14/lib-dynload/_ssl.cpython-314-darwin.so

install_name_tool \
    -change $ORIG_LIB/libcrypto.3.dylib $RPATH_LIB/libcrypto.3.dylib \
    $COPIED_LIB/python3.14/lib-dynload/_hashlib.cpython-314-darwin.so

# update curses links
install_name_tool \
    -id \
    $RPATH_LIB/libncurses.6.dylib \
    $COPIED_LIB/libncurses.dylib

install_name_tool \
    -id $RPATH_LIB/libform.6.dylib \
    -change $ORIG_LIB/libncurses.6.dylib $RPATH_LIB/libncurses.6.dylib \
    -change $ORIG_LIB/libform.6.dylib $RPATH_LIB/libform.6.dylib \
    $COPIED_LIB/libform.dylib

install_name_tool \
    -id $RPATH_LIB/libmenu.6.dylib \
    -change $ORIG_LIB/libncurses.6.dylib $RPATH_LIB/libncurses.6.dylib \
    -change $ORIG_LIB/libmenu.6.dylib $RPATH_LIB/libmenu.6.dylib \
    $COPIED_LIB/libmenu.dylib

install_name_tool \
    -id $RPATH_LIB/libpanel.6.dylib \
    -change $ORIG_LIB/libncurses.6.dylib $RPATH_LIB/libncurses.6.dylib \
    -change $ORIG_LIB/libpanel.6.dylib $RPATH_LIB/libpanel.6.dylib \
    $COPIED_LIB/libpanel.dylib

install_name_tool \
    -change $ORIG_LIB/libncurses.6.dylib $RPATH_LIB/libncurses.6.dylib \
    $COPIED_LIB/python3.14/lib-dynload/_curses.cpython-314-darwin.so

install_name_tool \
    -change $ORIG_LIB/libncurses.6.dylib $RPATH_LIB/libncurses.6.dylib \
    -change $ORIG_LIB/libpanel.6.dylib $RPATH_LIB/libpanel.6.dylib \
    $COPIED_LIB/python3.14/lib-dynload/_curses_panel.cpython-314-darwin.so


# libzstd

install_name_tool \
    -id $RPATH_LIB/libzstd.1.dylib \
    -change $ORIG_LIB/libzstd.1.dylib $RPATH_LIB/libzstd.1.dylib \
    $COPIED_LIB/libzstd.1.dylib

install_name_tool \
    -change $ORIG_LIB/libzstd.1.dylib $RPATH_LIB/libzstd.1.dylib \
    $COPIED_LIB/python3.14/lib-dynload/_zstd.cpython-314-darwin.so


# copy the token signifying Thonny-private Python
cp thonny_python.ini $NEW_FRAMEWORK_PATH/Versions/$VERSION/bin

# create link to Current version (required by codesign)
cd $LOCAL_FRAMEWORKS/Python.framework/Versions
ln -s $VERSION Current
