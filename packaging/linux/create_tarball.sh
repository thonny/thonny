#!/bin/bash

set -e

PREFIX=$HOME/pythonny

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# prepare working folder
rm -rf build
TARGET_DIR=build/thonny
mkdir -p $TARGET_DIR




# copy files
cp -r $PREFIX/* $TARGET_DIR
cp install.py $TARGET_DIR/install.py
cp install.sh $TARGET_DIR/install

# copy the token signifying Thonny-private Python
cp thonny_python.ini $TARGET_DIR/bin 

mkdir -p $TARGET_DIR/templates
cp uninstall.sh $TARGET_DIR/templates
cp Thonny.desktop $TARGET_DIR/templates

export LD_LIBRARY_PATH=$TARGET_DIR/lib

# Upgrade pip ##########################################
$TARGET_DIR/bin/python3.6 -m pip install --upgrade pip

# INSTALL DEPS ###################################
$TARGET_DIR/bin/python3.6 -m pip install jedi==0.10.2
$TARGET_DIR/bin/python3.6 -m pip install --no-cache-dir distro
$TARGET_DIR/bin/python3.6 -m pip install --no-cache-dir certifi

# INSTALL THONNY ###################################
$TARGET_DIR/bin/python3.6 -m pip install --pre --no-cache-dir thonny

VERSION=$(<$TARGET_DIR/lib/python3.6/site-packages/thonny/VERSION)
ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 


# clean up unnecessary stuff
rm -rf $TARGET_DIR/share
rm -rf $TARGET_DIR/man
rm -rf $TARGET_DIR/openssl

find $TARGET_DIR -type f -name "*.a" -delete
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete

rm -rf $TARGET_DIR/lib/tk8.6/demos


#rm -rf $TARGET_DIR/lib/python3.6/test
rm -rf $TARGET_DIR/lib/python3.6/idlelib
rm -rf $TARGET_DIR/lib/python3.6/distutils/command/*.exe
#rm -rf $TARGET_DIR/lib/python3.6/config-3.6m
#rm -rf $TARGET_DIR/lib/python3.6/site-packages/pip*
#rm -rf $TARGET_DIR/lib/python3.6/site-packages/setuptools*


# clear most of the include folder ##################################################
rm -rf $TARGET_DIR/include/lzma
rm -rf $TARGET_DIR/include/*.h
mv $TARGET_DIR/include/python3.6m/pyconfig.h $SCRIPT_DIR # pip needs this
rm $TARGET_DIR/include/python3.6m/*
mv $SCRIPT_DIR/pyconfig.h $TARGET_DIR/include/python3.6m # put it back



# clear bin because its scripts have absolute paths #################################
mv $TARGET_DIR/bin/python3.6 $SCRIPT_DIR # save python exe
rm -rf $TARGET_DIR/bin/*
mv $SCRIPT_DIR/python3.6 $TARGET_DIR/bin/

# create new commands ###############################################################
cp thonny $TARGET_DIR/bin
cd $TARGET_DIR/bin
ln -s pip3.6 pip3
ln -s python3.6 python3
cd $SCRIPT_DIR



# copy licenses
cp ../../*LICENSE.txt $TARGET_DIR

# put it together
mkdir -p dist
tar -cvzf dist/$VERSION_NAME.tar.gz -C build thonny


# create download + install script
DOWNINSTALL_FILENAME=thonny-$VERSION.sh

DOWNINSTALL_TARGET=dist/$DOWNINSTALL_FILENAME
cp downinstall_template.sh $DOWNINSTALL_TARGET
sed -i "s/VERSION/$VERSION/g" $DOWNINSTALL_TARGET

