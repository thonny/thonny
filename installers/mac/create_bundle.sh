#!/bin/bash

SOURCE_DIR=../..
VERSION=$(<$SOURCE_DIR/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 

# prepare working folder #########################################################
rm -rf cx_build
rm -rf build
mkdir -p build


# Freeze #########################################################################
PYTHON=/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5
$PYTHON ../cx_freeze/setup.py build -b cx_build > freezing.log

# move some dirs to correct location ##################
OUTPUT_DIR=cx_build/$(ls cx_build)
mv $OUTPUT_DIR/lib/VERSION $OUTPUT_DIR
mv $OUTPUT_DIR/lib/res $OUTPUT_DIR
mv $OUTPUT_DIR/lib/backend_private $OUTPUT_DIR


# fix absolute path dependency on Python #########################################
install_name_tool -change /Library/Frameworks/Python.framework/Versions/3.5/Python \
	@executable_path/Python \
	$OUTPUT_DIR/thonny_frontend
	
install_name_tool -change /Library/Frameworks/Python.framework/Versions/3.5/Python \
	@executable_path/Python \
	$OUTPUT_DIR/thonny_backend

install_name_tool -change /Library/Frameworks/Tcl.framework/Versions/8.6/Tcl \
    @executable_path/../Frameworks/Tcl.framework/Versions/8.6/Tcl \
    $OUTPUT_DIR/lib/python3.5/_tkinter.cpython-35m-darwin.so
       
install_name_tool -change /Library/Frameworks/Tk.framework/Versions/8.6/Tk \
    @executable_path/../Frameworks/Tk.framework/Versions/8.6/Tk \
    $OUTPUT_DIR/lib/python3.5/_tkinter.cpython-35m-darwin.so
    
#cp -R ~/Downloads/build/tcl/Tcl.framework/Versions/8.6/Resources/Scripts/* tcl
       
# copy template and source files #################################################
cp -r Thonny.app.template build/Thonny.app
#mv build/Thonny.app.template build/Thonny.app

mkdir -p build/Thonny.app/Contents/MacOS 
cp -r $OUTPUT_DIR/* build/Thonny.app/Contents/MacOS


# get and set version ############################################################
VERSION=$(<../../VERSION)
sed -i.bak "s/VERSION/$VERSION/" build/Thonny.app/Contents/Info.plist
rm -f build/Thonny.app/Contents/Info.plist.bak

# add readme #####################################################################
cp readme.txt build

# create dmg #####################################################################
mkdir -p dist
FILENAME=dist/thonny-$VERSION.dmg
rm -f $FILENAME
hdiutil create -srcfolder build -volname "Thonny $VERSION" $FILENAME
hdiutil internet-enable -yes $FILENAME

