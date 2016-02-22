#!/usr/bin/env bash

# This version takes official Python installation as base

export REGULAR_USER=$(whoami)
export PREFIX=$HOME/pythonny_alt
export RELATIVE_LIBDIR=@executable_path/../lib
MAIN_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
export TEMP_BUILD_DIR=$MAIN_DIR/temp_build_dir




rm -rf $TEMP_BUILD_DIR
mkdir $TEMP_BUILD_DIR
cd $TEMP_BUILD_DIR

# NB! If you update xcode then first do:
# sudo xcodebuild -license

rm -rf $PREFIX
mkdir $PREFIX

$MAIN_DIR/copy_python.sh
cd $TEMP_BUILD_DIR



# _tkinter #####################################################################
$MAIN_DIR/build_tcltk.sh 8.6
cd $TEMP_BUILD_DIR

# Link _tkinter to newly built Tcl/Tk
# assuming it is originally linked to 8.5

install_name_tool -change \
    /Library/Frameworks/Tcl.framework/Versions/8.5/Tcl \
	$RELATIVE_LIBDIR/Tcl \
    $PREFIX/lib/python3.5/lib-dynload/_tkinter.cpython-35m-darwin.so 

install_name_tool -change \
    /Library/Frameworks/Tk.framework/Versions/8.5/Tk \
	$RELATIVE_LIBDIR/Tk \
    $PREFIX/lib/python3.5/lib-dynload/_tkinter.cpython-35m-darwin.so 

cd $MAIN_DIR


    
