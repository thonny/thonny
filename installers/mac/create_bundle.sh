#!/bin/bash

PLATFORM_ID=exe.macosx-10.6-intel-3.4

# prepare working folder #########################################################
rm -rf cx_build
rm -rf build
mkdir -p build

# Freeze #########################################################################
python3 ../cx_freeze/setup.py build -b cx_build > freezing.log

# fix absolute path dependency on Python #########################################
install_name_tool -change /Library/Frameworks/Python.framework/Versions/3.4/Python \
	@executable_path/Python \
	cx_build/$PLATFORM_ID/thonny_frontend
	
install_name_tool -change /Library/Frameworks/Python.framework/Versions/3.4/Python \
	@executable_path/Python \
	cx_build/$PLATFORM_ID/thonny_backend

# copy template and source files #################################################
cp -r Thonny.app.template build/Thonny.app
#mv build/Thonny.app.template build/Thonny.app

mkdir -p build/Thonny.app/Contents/MacOS 
cp -r cx_build/$PLATFORM_ID/* build/Thonny.app/Contents/MacOS


# get and set version ############################################################
VERSION=$(<../../VERSION)
sed -i.bak "s/VERSION/$VERSION/" build/Thonny.app/Contents/Info.plist
rm -f build/Thonny.app/Contents/Info.plist.bak


# create dmg #####################################################################
mkdir -p dist
FILENAME=dist/thonny-$VERSION.dmg
rm -f $FILENAME
hdiutil create -srcfolder build $FILENAME
hdiutil internet-enable -yes $FILENAME

