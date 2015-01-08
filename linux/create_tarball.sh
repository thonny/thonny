#!/bin/bash

# prepare working folder
rm -rf build
mkdir -p build

# copy template and source files
VERSION=$(<../thonny/VERSION)
VERSION_NAME=thonny-$VERSION 
MAIN_DIR=build/$VERSION_NAME
mkdir $MAIN_DIR

cp -r ../thonny $MAIN_DIR
cp Thonny.desktop $MAIN_DIR
cp thonny.sh $MAIN_DIR
cp install.py $MAIN_DIR/install
chmod 755 $MAIN_DIR/install

# clean up unnecessary stuff
rm -rf $MAIN_DIR/thonny/__pycache__
rm -rf $MAIN_DIR/thonny/*.pyo
rm -rf $MAIN_DIR/thonny/*.pyc 

# put it together
mkdir -p dist
tar -cvzf dist/thonny-$VERSION.tar.gz -C build $VERSION_NAME

