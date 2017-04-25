#!/bin/bash
set -e

# Should be run after new thonny package is uploaded to PyPi

PREFIX=$HOME/thonny_template_build
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template #################################################
cp -R -H $PREFIX/Thonny.app build

# update launch script (might have changed after last create_base_bundle.sh) #####################
cp $SCRIPT_DIR/Thonny.app.initial_template/Contents/MacOS/thonny \
    build/Thonny.app/Contents/MacOS

FRAMEWORKS=build/Thonny.app/Contents/Frameworks
PYTHON_CURRENT=$FRAMEWORKS/Python.framework/Versions/3.6/

# install jedi #####################################################
$PYTHON_CURRENT/bin/python3.6 -m pip install jedi==0.10.2

# install certifi #####################################################
$PYTHON_CURRENT/bin/python3.6 -m pip install certifi

# install thonny #####################################################
$PYTHON_CURRENT/bin/python3.6 -m pip install --pre --no-cache-dir thonny
rm $PYTHON_CURRENT/bin/thonny # because this contains absolute paths

# clean unnecessary stuff ###################################################

# delete all *.h files except one
mv $PYTHON_CURRENT/include/python3.6m/pyconfig.h $SCRIPT_DIR # pip needs this
find $FRAMEWORKS -name '*.h' -delete
mv $SCRIPT_DIR/pyconfig.h $PYTHON_CURRENT/include/python3.6m # put it back

find $FRAMEWORKS -name '*.a' -delete

rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.5/Tcl_debug
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.5/Tk_debug
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.5/Resources/Scripts/demos
rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.5/Resources/Documentation
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.5/Resources/Documentation

find $PYTHON_CURRENT/lib -name '*.pyc' -delete
find $PYTHON_CURRENT/lib -name '*.exe' -delete
rm -rf $PYTHON_CURRENT/Resources/English.lproj/Documentation

rm -rf $PYTHON_CURRENT/share
rm -rf $PYTHON_CURRENT/lib/python3.6/test
rm -rf $PYTHON_CURRENT/lib/python3.6/idlelib

# clear bin because its scripts have absolute paths
mv $PYTHON_CURRENT/bin/python3.6 $SCRIPT_DIR # save python exe
rm -rf $PYTHON_CURRENT/bin/*
mv $SCRIPT_DIR/python3.6 $PYTHON_CURRENT/bin/

# create new commands ###############################################################
cd $PYTHON_CURRENT/bin
ln -s python3.6 python3
cd $SCRIPT_DIR

# Replace Python.app Info.plist to get name "Thonny" to menubar
cp -f $SCRIPT_DIR/Python.app.plist $PYTHON_CURRENT/Resources/Python.app/Contents/Info.plist

# version info ##############################################################
VERSION=$(<$PYTHON_CURRENT/lib/python3.6/site-packages/thonny/VERSION)
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

