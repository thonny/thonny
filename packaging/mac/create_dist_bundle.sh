#!/bin/bash

PREFIX=$HOME/thonny_template_build


# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template #################################################
cp -R -H $PREFIX/Thonny.app build

FRAMEWORKS=build/Thonny.app/Contents/Frameworks
PYTHON_CURRENT=$FRAMEWORKS/Python.framework/Versions/3.5/

# install thonny #####################################################
$PYTHON_CURRENT/bin/python3.5 -m pip install --pre --no-cache-dir thonny
rm $PYTHON_CURRENT/bin/thonny # because this contains absolute paths

# install easygui (TODO: temp) #####################################################
$PYTHON_CURRENT/bin/python3.5 -m pip install --no-cache-dir easygui


# clean unnecessary stuff ###################################################

find $FRAMEWORKS -name '*.h' -delete
find $FRAMEWORKS -name '*.a' -delete

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
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/pip*

rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/numpy/lib/tests
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/numpy/core/tests
rm -rf $PYTHON_CURRENT/lib/python3.5/site-packages/numpy/ma/tests


rm $PYTHON_CURRENT/bin/2to3-3.5
rm $PYTHON_CURRENT/bin/easy_install-3.5
rm $PYTHON_CURRENT/bin/idle3.5
rm $PYTHON_CURRENT/bin/idle3
rm $PYTHON_CURRENT/bin/pip3.5
rm $PYTHON_CURRENT/bin/pip3
rm $PYTHON_CURRENT/bin/pydoc3.5
rm $PYTHON_CURRENT/bin/python3
rm $PYTHON_CURRENT/bin/python3-32
rm $PYTHON_CURRENT/bin/python3.5-32
rm $PYTHON_CURRENT/bin/python3-config
rm $PYTHON_CURRENT/bin/python3.5-config
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

