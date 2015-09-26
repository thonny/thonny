#!/bin/bash

# prepare working folder
rm -rf cx_build
rm -rf build
mkdir -p build

python3.4 ../cx_freeze/setup.py build -b cx_build > freezing.log

# copy template and source files
VERSION=$(<../../VERSION)
VERSION_NAME=thonny-$VERSION 
MAIN_DIR=build/$VERSION_NAME
mkdir $MAIN_DIR

cp -r cx_build/exe.linux-i686-3.4/* $MAIN_DIR
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

