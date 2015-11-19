#!/bin/bash

PREFIX=/home/aivar/pythonny


# INSTALL/UPDATE THONNY ###################################
$PREFIX/bin/python3.5 -m pip install --upgrade thonny

VERSION=$(<$PREFIX/lib/python3.5/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 

# prepare working folder
rm -rf build
TARGET_DIR=build/thonny
mkdir -p $TARGET_DIR




# copy files
cp -r $PREFIX/* $TARGET_DIR
cp thonny $TARGET_DIR/bin
cp install.py $TARGET_DIR/install

mkdir -p $TARGET_DIR/templates
cp uninstall.sh $TARGET_DIR/templates
cp Thonny.desktop $TARGET_DIR/templates


# clean up unnecessary stuff
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete
rm -rf $TARGET_DIR/include
rm -rf $TARGET_DIR/lib/python3.5/config-3.5m
rm -rf $TARGET_DIR/lib/python3.5/ensurepip
rm -rf $TARGET_DIR/lib/python3.5/site-packages/pip*
rm -rf $TARGET_DIR/lib/python3.5/site-packages/setuptools*



# put it together
mkdir -p dist
tar -cvzf dist/$VERSION_NAME.tar.gz -C build thonny

