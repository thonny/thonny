#!/bin/bash

# Should be run after new thonny package is uploaded to PyPi

PREFIX=$HOME/thonny_template_build
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template #################################################
cp -R -H $PREFIX/Thonny.app build

FRAMEWORKS=build/Thonny.app/Contents/Frameworks
PYTHON_CURRENT=$FRAMEWORKS/Python.framework/Versions/3.5/

# Upgrade pip ##########################################
$PYTHON_CURRENT/bin/python3.5 -m pip install --upgrade pip

# install thonny #####################################################
$PYTHON_CURRENT/bin/python3.5 -m pip install --pre --no-cache-dir thonny
rm $PYTHON_CURRENT/bin/thonny # because this contains absolute paths

# clean unnecessary stuff ###################################################
# /include/python3.5m/pyconfig.h
#find $FRAMEWORKS -name '*.h' -delete
#find $FRAMEWORKS -name '*.a' -delete

rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.5/Tcl_debug
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.5/Tk_debug
rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.5/Resources/Documentation
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.5/Resources/Documentation

rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.6/Tcl_debug
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.6/Tk_debug
rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.6/Resources/Documentation
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.6/Resources/Documentation


find $PYTHON_CURRENT/lib -name '*.pyc' -delete
find $PYTHON_CURRENT/lib -name '*.exe' -delete
rm -rf $PYTHON_CURRENT/Resources/English.lproj/Documentation

rm -rf $PYTHON_CURRENT/share
rm -rf $PYTHON_CURRENT/lib/python3.5/test
rm -rf $PYTHON_CURRENT/lib/python3.5/ensurepip
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/pygame/examples
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/pygame/tests
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/pygame/docs

rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/tkinterhtml/tkhtml/Windows
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/tkinterhtml/tkhtml/Linux
rm -rf $PYTHON_CURRENT/lib/python3.5/idlelib


# clear bin because its scripts have absolute paths
mv $PYTHON_CURRENT/bin/python3.5 $DIR # save python exe
rm -rf $PYTHON_CURRENT/bin/*
mv $DIR/python3.5 $PYTHON_CURRENT/bin/

# create new commands ###############################################################
cp pip.sh $PYTHON_CURRENT/bin/pip3.5
cd $PYTHON_CURRENT/bin
ln -s pip3.5 pip3
ln -s python3.5 python3
cd $DIR

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

