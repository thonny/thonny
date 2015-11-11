#!/bin/bash

SOURCE_PREFIX=/opt/pythonny

# update thonny installation #####################################################
$SOURCE_PREFIX/bin/python3.5 -m pip install --force-reinstall thonny
rm $SOURCE_PREFIX/bin/thonny


VERSION=$(<$SOURCE_PREFIX/lib/python3.5/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 

# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template and source files #################################################
cp -r Thonny.app.template build/Thonny.app

mkdir -p build/Thonny.app/Contents/MacOS 
cp -r $SOURCE_PREFIX/* build/Thonny.app/Contents/MacOS


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

