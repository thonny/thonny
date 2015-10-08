#!/bin/bash

SOURCE_DIR=../..

VERSION=$(<$SOURCE_DIR/VERSION)
VERSION_NAME=thonny-$VERSION 

# prepare working folder
rm -rf build
TARGET_DIR=build/$VERSION_NAME
mkdir -p $TARGET_DIR



# copy files
cp $SOURCE_DIR/license_wrapped.txt $TARGET_DIR/license.txt
cp readme.txt $TARGET_DIR/readme.txt
cp install.py $TARGET_DIR/install
chmod 755 $TARGET_DIR/install

mkdir -p $TARGET_DIR/share
cp -r $SOURCE_DIR/thonny_frontend.py $TARGET_DIR/share
cp -r $SOURCE_DIR/thonny_backend.py $TARGET_DIR/share
cp -r $SOURCE_DIR/VERSION $TARGET_DIR/share
cp -r $SOURCE_DIR/thonny $TARGET_DIR/share
cp -r $SOURCE_DIR/rope $TARGET_DIR/share
cp -r $SOURCE_DIR/jedi $TARGET_DIR/share
cp -r $SOURCE_DIR/res $TARGET_DIR/share

mkdir -p $TARGET_DIR/share/backend_private
cp -r $SOURCE_DIR/thonny_backend.py $TARGET_DIR/share/backend_private
cp -r $SOURCE_DIR/thonny/backend.py $TARGET_DIR/share/backend_private
cp -r $SOURCE_DIR/thonny/ast_utils.py $TARGET_DIR/share/backend_private
cp -r $SOURCE_DIR/thonny/misc_utils.py $TARGET_DIR/share/backend_private
cp -r $SOURCE_DIR/thonny/common.py $TARGET_DIR/share/backend_private

#mkdir -fp $TARGET_DIR/share/backend_private

mkdir -p $TARGET_DIR/templates
cp thonny.sh $TARGET_DIR/templates
cp uninstall.sh $TARGET_DIR/templates
cp Thonny.desktop $TARGET_DIR/templates


# clean up unnecessary stuff
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete

# put it together
mkdir -p dist
tar -cvzf dist/thonny-$VERSION.tar.gz -C build $VERSION_NAME

