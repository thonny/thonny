#!/bin/bash

PREFIX=/Users/aivar/pythonny


# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template and source files #################################################
cp -r Thonny.app.template build/Thonny.app

MACOS_PATH=build/Thonny.app/Contents/MacOS
mkdir -p $MACOS_PATH 
cp -r $PREFIX/* $MACOS_PATH

# update/install thonny #####################################################
$MACOS_PATH/bin/python3.5 -m pip install --force-reinstall thonny
rm $MACOS_PATH/bin/thonny # because this contains absolute paths

# clean unnecessary stuff we don't need after installing thonny
rm -rf $MACOS_PATH/lib/python3.5/config-3.5m
rm -rf $MACOS_PATH/lib/python3.5/site-packages/pip
rm -rf $MACOS_PATH/lib/python3.5/ensurepip

# version info ##############################################################
VERSION=$(<$MACOS_PATH/lib/python3.5/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 


# set version ############################################################
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

