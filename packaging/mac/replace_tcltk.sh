#!/usr/bin/env bash

DST=/Library/Frameworks/Python.framework/Versions/Current/lib

# Tcl
SRC=/Library/Frameworks/Tcl.framework/Versions/8.6
cp $SRC/Tcl $DST/libtcl8.6.dylib
cp $SRC/libtclstub8.6.a $DST
#cp $SRC/*.sh $DST
cp -rf $SRC/Resources/tcl8 $DST
cp -rf $SRC/Resources/Scripts/* $DST/tcl8.6

# Tk
SRC=/Library/Frameworks/Tk.framework/Versions/8.6
cp $SRC/Tk $DST/libtk8.6.dylib
cp $SRC/libtkstub8.6.a $DST
#cp $SRC/*.sh $DST
cp -rf $SRC/Resources/Scripts $DST/tk8.6



