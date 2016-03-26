#!/usr/bin/env bash

PREFIX=/Users/aivar/pythonny3
LOCAL_FRAMEWORKS=$PREFIX/Thonny.app/Contents/Frameworks

# This must point to tkinter compiled against Tk 8.6
TKINTER_FILENAME=_tkinter.cpython-35m-darwin.so
LOCAL_TKINTER=$LOCAL_FRAMEWORKS/Python.framework/Versions/3.5/lib/python3.5/lib-dynload/$TKINTER_FILENAME
TKINTER86=/Users/aivar/pythonny/lib/python3.5/lib-dynload/$TKINTER_FILENAME
cp -f $TKINTER86 $LOCAL_TKINTER

chmod u+w $LOCAL_TKINTER


# _tkinter ##########################
install_name_tool -change \
    /Library/Frameworks/Tcl.framework/Versions/8.6/Tcl \
	@rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_TKINTER 

install_name_tool -change \
    /Library/Frameworks/Tk.framework/Versions/8.6/Tk \
	@rpath/Tk.framework/Versions/8.6/Tk \
    $LOCAL_TKINTER 

# TODO: temp
install_name_tool -change \
    @executable_path/../lib/Tcl \
	@rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_TKINTER 

install_name_tool -change \
    @executable_path/../lib/Tk \
	@rpath/Tk.framework/Versions/8.6/Tk \
    $LOCAL_TKINTER 
