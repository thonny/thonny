#!/bin/bash
set -e
# https://github.com/lektor/lektor/blob/master/gui/bin/make-python-framework-relocatable

# Take from env
# LOCAL_FRAMEWORKS=$HOME/thonny_template_build/Thonny.app/Contents/Frameworks

VERSION=3.6
ORIGINAL_FRAMEWORK_PATH=/Library/Frameworks/Python.framework
NEW_FRAMEWORK_PATH=$LOCAL_FRAMEWORKS/Python.framework

rm -rf $NEW_FRAMEWORK_PATH
mkdir -p $NEW_FRAMEWORK_PATH

cp -R $ORIGINAL_FRAMEWORK_PATH/* $NEW_FRAMEWORK_PATH

BIN_EXE=$NEW_FRAMEWORK_PATH/Versions/$VERSION/bin/python$VERSION

# delete everything in bin except python3.6
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

# TODO: update curses libraries links in lib


# update tkinter links
TKINTER_FILENAME=_tkinter.cpython-36m-darwin.so
LOCAL_TKINTER=$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/$TKINTER_FILENAME

install_name_tool -change \
    /Library/Frameworks/Tcl.framework/Versions/8.5/Tcl \
	@rpath/Tcl.framework/Versions/8.5/Tcl \
    $LOCAL_TKINTER 

install_name_tool -change \
    /Library/Frameworks/Tk.framework/Versions/8.5/Tk \
	@rpath/Tk.framework/Versions/8.5/Tk \
    $LOCAL_TKINTER 

# update libcrypto and libssl links
install_name_tool -id \
	@rpath/Python.framework/Versions/3.6/lib/libcrypto.1.0.0.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libcrypto.1.0.0.dylib 

install_name_tool -id \
	@rpath/Python.framework/Versions/3.6/lib/libssl.1.0.0.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libssl.1.0.0.dylib 

install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libcrypto.1.0.0.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libcrypto.1.0.0.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libssl.1.0.0.dylib

install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libcrypto.1.0.0.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libcrypto.1.0.0.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/_ssl.cpython-36m-darwin.so

install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libssl.1.0.0.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libssl.1.0.0.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/_ssl.cpython-36m-darwin.so

# update curses links
install_name_tool -id \
	@rpath/Python.framework/Versions/3.6/lib/libncursesw.5.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libncursesw.5.dylib 

install_name_tool -id \
	@rpath/Python.framework/Versions/3.6/lib/libformw.5.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libformw.5.dylib 
install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libformw.5.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libformw.5.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libformw.5.dylib

install_name_tool -id \
	@rpath/Python.framework/Versions/3.6/lib/libmenuw.5.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libmenuw.5.dylib 
install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libmenuw.5.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libmenuw.5.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libmenuw.5.dylib

install_name_tool -id \
	@rpath/Python.framework/Versions/3.6/lib/libpanelw.5.dylib \
    $LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libpanelw.5.dylib 
install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libpanelw.5.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libpanelw.5.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/libpanelw.5.dylib

install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libncursesw.5.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libncursesw.5.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/_curses.cpython-36m-darwin.so

install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libncursesw.5.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libncursesw.5.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/_curses_panel.cpython-36m-darwin.so
install_name_tool -change \
	/Library/Frameworks/Python.framework/Versions/3.6/lib/libpanelw.5.dylib \
	@rpath/Python.framework/Versions/3.6/lib/libpanelw.5.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.6/lib/python3.6/lib-dynload/_curses_panel.cpython-36m-darwin.so


# copy the token signifying Thonny-private Python
cp thonny_python.ini $NEW_FRAMEWORK_PATH/Versions/$VERSION/bin 

# create link to Current version (required by codesign)
cd $LOCAL_FRAMEWORKS/Python.framework/Versions
ln -s $VERSION Current