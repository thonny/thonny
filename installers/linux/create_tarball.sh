#!/bin/bash

SOURCE_DIR=../..

VERSION=$(<$SOURCE_DIR/VERSION)
VERSION_NAME=thonny-$VERSION 

# prepare working folder
rm -rf build
TARGET_DIR=build/$VERSION_NAME
mkdir -p $TARGET_DIR

# copy source and template files
mkdir -p $TARGET_DIR/share
cp -r $SOURCE_DIR/thonny_frontend.py $TARGET_DIR/share
cp -r $SOURCE_DIR/thonny_backend.py $TARGET_DIR/share
cp -r $SOURCE_DIR/VERSION $TARGET_DIR/share
cp -r $SOURCE_DIR/thonny $TARGET_DIR/share
cp -r $SOURCE_DIR/rope $TARGET_DIR/share
cp -r $SOURCE_DIR/jedi $TARGET_DIR/share
cp -r $SOURCE_DIR/res $TARGET_DIR/share

cp thonny.sh $TARGET_DIR/bin/thonny
cp thonny.sh $TARGET_DIR/bin/thonny
 

cp -r $SOURCE_DIR/LICENSE $TARGET_DIR
cp INSTALL $TARGET_DIR
cp Thonny.desktop $TARGET_DIR/temp
cp uninstall.sh $TARGET_DIR/temp

cp install.py $TARGET_DIR/install
chmod 755 $TARGET_DIR/install

# clean up unnecessary stuff
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete

# put it together
mkdir -p dist
tar -cvzf dist/thonny-$VERSION.tar.gz -C build $VERSION_NAME

