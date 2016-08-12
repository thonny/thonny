#!/bin/bash

set -e

PREFIX=$HOME/pythonny



# prepare working folder
rm -rf build
TARGET_DIR=build/thonny
mkdir -p $TARGET_DIR




# copy files
cp -r $PREFIX/* $TARGET_DIR
cp install.py $TARGET_DIR/install.py
cp install.sh $TARGET_DIR/install

mkdir -p $TARGET_DIR/templates
cp uninstall.sh $TARGET_DIR/templates
cp Thonny.desktop $TARGET_DIR/templates

export LD_LIBRARY_PATH=$TARGET_DIR/lib

# Upgrade pip ##########################################
$TARGET_DIR/bin/python3.5 -m pip install --upgrade pip

# INSTALL THONNY ###################################
$TARGET_DIR/bin/python3.5 -m pip install --pre --no-cache-dir thonny

# INSTALL EASYGUI (TODO: temp) ###################################
$TARGET_DIR/bin/python3.5 -m pip install --no-cache-dir easygui

# INSTALL PYGAME ###################################
$TARGET_DIR/bin/python3.5 -m pip install --no-cache-dir pygame

VERSION=$(<$TARGET_DIR/lib/python3.5/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 


# clean up unnecessary stuff
rm -rf $TARGET_DIR/share
rm -rf $TARGET_DIR/man
rm -rf $TARGET_DIR/openssl/man
rm -rf $TARGET_DIR/include/openssl

#find $TARGET_DIR -type f -name "*.a" -delete
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete

rm -rf $TARGET_DIR/lib/python3.5/ensurepip
#rm -rf $TARGET_DIR/include
#rm -rf $TARGET_DIR/lib/python3.5/config-3.5m
#rm -rf $TARGET_DIR/lib/python3.5/site-packages/pip*
#rm -rf $TARGET_DIR/lib/python3.5/site-packages/setuptools*

rm -rf $TARGET_DIR/lib/python3.5/site-packages/tkinterhtml/tkhtml/Windows
rm -rf $TARGET_DIR/lib/python3.5/site-packages/tkinterhtml/tkhtml/MacOSX

# clear bin because its scripts have absolute paths
mv $PYTHON_CURRENT/bin/python3.5 $DIR # save python exe
rm -rf $PYTHON_CURRENT/bin/*
mv $DIR/python3.5 $PYTHON_CURRENT/bin/

# create new commands ###############################################################
cp thonny $TARGET_DIR/bin
cp pip.sh $TARGET_DIR/bin/pip3.5
cd $TARGET_DIR/bin
ln -s pip3.5 pip3
ln -s python3.5 python3
cd $DIR



# copy licenses
cp ../../*LICENSE.txt $TARGET_DIR

# put it together
mkdir -p dist
tar -cvzf dist/$VERSION_NAME.tar.gz -C build thonny

