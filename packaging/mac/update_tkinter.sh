#!/usr/bin/env bash

# take from env
# LOCAL_FRAMEWORKS=$HOME/thonny_template_build/Thonny.app/Contents/Frameworks

# Official tkinter is compiled against Tk 8.5, I want 8.6
# Assuming $HOME/build contains Python compiled against Tk 8.6
TKINTER_FILENAME=_tkinter.cpython-35m-darwin.so
LOCAL_TKINTER=$LOCAL_FRAMEWORKS/Python.framework/Versions/3.5/lib/python3.5/lib-dynload/$TKINTER_FILENAME
TKINTER86=$PREFIX/lib/python3.5/lib-dynload/$TKINTER_FILENAME
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

