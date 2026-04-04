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
ORIG_MAIN_LIB=$ORIGINAL_FRAMEWORK_PATH/Versions/$VERSION/Python
NEW_MAIN_LIB=$NEW_FRAMEWORK_PATH/Versions/$VERSION/Python
MAIN_LIB_LOCAL_NAME=@rpath/Python.framework/Versions/$VERSION/Python

chmod u+w $NEW_MAIN_LIB $BIN_EXE $BUNDLE_EXE

install_name_tool -change $ORIG_MAIN_LIB $MAIN_LIB_LOCAL_NAME $BIN_EXE
install_name_tool -add_rpath @executable_path/../../../../ $BIN_EXE

install_name_tool -id @rpath/Python.framework/Versions/$VERSION/Python $NEW_MAIN_LIB


install_name_tool -change $ORIG_MAIN_LIB $MAIN_LIB_LOCAL_NAME $BUNDLE_EXE
install_name_tool -add_rpath @executable_path/../../../../../../../ $BUNDLE_EXE

# update tkinter links
chmod 0755 $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Versions/8.6/Tcl
install_name_tool -id \
    @rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Versions/8.6/Tcl

chmod 0755 $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tk.framework/Versions/8.6/Tk
install_name_tool -id \
    @rpath/Tk.framework/Versions/8.6/Tk \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tk.framework/Versions/8.6/Tk

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Versions/8.6/Tcl \
    @rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/Frameworks/Tk.framework/Versions/8.6/Tk

install_name_tool -add_rpath \
    @loader_path/../../../Frameworks \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_tkinter.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/Frameworks/Tcl.framework/Versions/8.6/Tcl \
    @rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_tkinter.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/Frameworks/Tk.framework/Versions/8.6/Tk \
    @rpath/Tk.framework/Versions/8.6/Tk \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_tkinter.cpython-314-darwin.so

# update libcrypto and libssl links
install_name_tool -id \
    @rpath/Python.framework/Versions/3.14/lib/libcrypto.3.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libcrypto.3.dylib

install_name_tool -id \
    @rpath/Python.framework/Versions/3.14/lib/libssl.3.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libssl.3.dylib

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libcrypto.3.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libcrypto.3.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libssl.3.dylib

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libcrypto.3.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libcrypto.3.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_ssl.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libssl.3.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libssl.3.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_ssl.cpython-314-darwin.so

# update curses links
install_name_tool -id \
    @rpath/Python.framework/Versions/3.14/lib/libncurses.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libncurses.dylib

install_name_tool -id \
    @rpath/Python.framework/Versions/3.14/lib/libform.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libform.dylib

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libform.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libform.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libform.dylib

install_name_tool -id \
    @rpath/Python.framework/Versions/3.14/lib/libmenu.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libmenu.dylib

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libmenu.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libmenu.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libmenu.dylib

install_name_tool -id \
    @rpath/Python.framework/Versions/3.14/lib/libpanel.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libpanel.dylib

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libpanel.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libpanel.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/libpanel.dylib

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libncurses.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libncurses.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_curses.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libncurses.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libncurses.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_curses_panel.cpython-314-darwin.so

install_name_tool -change \
    /Library/Frameworks/Python.framework/Versions/3.14/lib/libpanel.dylib \
    @rpath/Python.framework/Versions/3.14/lib/libpanel.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.14/lib/python3.14/lib-dynload/_curses_panel.cpython-314-darwin.so

# copy the token signifying Thonny-private Python
cp thonny_python.ini $NEW_FRAMEWORK_PATH/Versions/$VERSION/bin

# create link to Current version (required by codesign)
cd $LOCAL_FRAMEWORKS/Python.framework/Versions
ln -s $VERSION Current
