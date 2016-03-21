#!/bin/bash

PREFIX=/Users/aivar/pythonny3


# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy raw bundle #################################################
cp -R -H $PREFIX/Thonny.app build

FRAMEWORKS=build/Thonny.app/Contents/Frameworks
PYTHON_CURRENT=$FRAMEWORKS/Python.framework/Versions/3.5/

# install thonny #####################################################
$PYTHON_CURRENT/bin/python3.5 -m pip install --pre --no-cache-dir thonny
rm $PYTHON_CURRENT/bin/thonny # because this contains absolute paths

# install easygui (TODO: temp) #####################################################
$PYTHON_CURRENT/bin/python3.5 -m pip install --no-cache-dir easygui


# clean unnecessary stuff ###################################################

find $PYTHON_CURRENT/lib -name '*.pyc' -delete
find $PYTHON_CURRENT/lib -name '*.exe' -delete

rm $PYTHON_CURRENT/bin/2to3-3.5
rm $PYTHON_CURRENT/bin/easy_install-3.5
rm $PYTHON_CURRENT/bin/idle3.5
rm $PYTHON_CURRENT/bin/pip3.5
rm $PYTHON_CURRENT/bin/pydoc3.5
rm $PYTHON_CURRENT/bin/python3.5m
rm $PYTHON_CURRENT/bin/python3.5m-config
rm $PYTHON_CURRENT/bin/pyvenv-3.5


# version info ##############################################################
VERSION=$(<$PYTHON_CURRENT/lib/python3.5/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 


# set version ############################################################
sed -i.bak "s/VERSION/$VERSION/" build/Thonny.app/Contents/Info.plist
rm -f build/Thonny.app/Contents/Info.plist.bak

# add readme #####################################################################
cp readme.txt build

# create dmg #####################################################################
mkdir -p dist
FILENAME=dist/thonny-${VERSION}.dmg
rm -f $FILENAME
hdiutil create -srcfolder build -volname "Thonny $VERSION" $FILENAME
hdiutil internet-enable -yes $FILENAME

