#!/bin/bash

PREFIX=$HOME/pythonny



# prepare working folder
rm -rf build
TARGET_DIR=build/thonny
mkdir -p $TARGET_DIR




# copy files
cp -r $PREFIX/* $TARGET_DIR
cp install.py $TARGET_DIR/install

mkdir -p $TARGET_DIR/templates
cp uninstall.sh $TARGET_DIR/templates
cp Thonny.desktop $TARGET_DIR/templates

export LD_LIBRARY_PATH=$TARGET_DIR/lib

# INSTALL THONNY ###################################
$TARGET_DIR/bin/python3.5 -m pip install --no-cache-dir thonny

# INSTALL EASYGUI (TODO: temp) ###################################
$TARGET_DIR/bin/python3.5 -m pip install --no-cache-dir easygui

VERSION=$(<$TARGET_DIR/lib/python3.5/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 

# override thonny launcher
rm $TARGET_DIR/bin/thonny
cp thonny $TARGET_DIR/bin


# clean up unnecessary stuff
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete
rm -rf $TARGET_DIR/include
rm -rf $TARGET_DIR/lib/python3.5/config-3.5m
rm -rf $TARGET_DIR/lib/python3.5/ensurepip
rm -rf $TARGET_DIR/lib/python3.5/site-packages/pip*
rm -rf $TARGET_DIR/lib/python3.5/site-packages/setuptools*

# copy licenses
cp ../../*LICENSE.txt $TARGET_DIR

# put it together
mkdir -p dist
tar -cvzf dist/$VERSION_NAME.tar.gz -C build thonny

