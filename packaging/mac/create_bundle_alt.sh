#!/bin/bash

PREFIX=/Users/aivar/pythonny_alt


# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template and source files #################################################
cp -R -H Thonny.app.template build/Thonny.app

MACOS_PATH=build/Thonny.app/Contents/MacOS
mkdir -p $MACOS_PATH 
cp -R -H $PREFIX/* $MACOS_PATH

# install thonny #####################################################
$MACOS_PATH/bin/python3.5 -m pip install --pre --no-cache-dir thonny
rm $MACOS_PATH/bin/thonny # because this contains absolute paths

# install easygui (TODO: temp) #####################################################
$MACOS_PATH/bin/python3.5 -m pip install --no-cache-dir easygui


# clean unnecessary stuff ###################################################
rm -rf $MACOS_PATH/share
rm -rf $MACOS_PATH/man
rm -rf $MACOS_PATH/Resources
rm -rf $MACOS_PATH/Headers
rm -rf $MACOS_PATH/lib/python3.5/__pycache__
rm -rf $MACOS_PATH/lib/python3.5/test
rm -f $MACOS_PATH/lib/*.a

find $MACOS_PATH/lib -name '*.pyc' -delete
find $MACOS_PATH/lib -name '*.exe' -delete

rm $MACOS_PATH/bin/2to3-3.5
rm $MACOS_PATH/bin/easy_install-3.5
rm $MACOS_PATH/bin/idle3.5
rm $MACOS_PATH/bin/pip3.5
rm $MACOS_PATH/bin/pydoc3.5
rm $MACOS_PATH/bin/python3.5m
rm $MACOS_PATH/bin/python3.5m-config
rm $MACOS_PATH/bin/pyvenv-3.5
rm $MACOS_PATH/bin/tclsh8.6
rm $MACOS_PATH/bin/wish8.6
rm $MACOS_PATH/bin/tclsh
rm $MACOS_PATH/bin/wish
rm $MACOS_PATH/bin/c_rehash
rm $MACOS_PATH/bin/*lz*
rm $MACOS_PATH/bin/*xz*
rm $MACOS_PATH/bin/*openssl*

rm -rf $MACOS_PATH/lib/tk8.6/demos


# TODO: keep these if you want to use pip in Thonny
rm -rf $MACOS_PATH/include
rm -rf $MACOS_PATH/lib/python3.5/config-3.5m
rm -rf $MACOS_PATH/lib/python3.5/site-packages/pip*
rm -rf $MACOS_PATH/lib/python3.5/site-packages/setuptools*

# Not sure if these are required for using pip
rm -rf $MACOS_PATH/lib/python3.5/ensurepip
rm -f $MACOS_PATH/lib/libpython3.5m.a




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
FILENAME=dist/thonny-${VERSION}_alt.dmg
rm -f $FILENAME
hdiutil create -srcfolder build -volname "Thonny $VERSION" $FILENAME
hdiutil internet-enable -yes $FILENAME

