#!/bin/bash

SOURCE_DIR=../..

VERSION=$(<$SOURCE_DIR/VERSION)
VERSION_NAME=thonny-$VERSION 

# Clean #########################################################################
# prepare working folder
rm -rf build
rm -rf cx_build

TARGET_DIR=build/$VERSION_NAME
mkdir -p $TARGET_DIR

# Freeze #########################################################################
/home/aivar/localpython/bin/python3 ../cx_freeze/setup.py build -b cx_build > freezing.log

# move some dirs to correct location ##################
OUTPUT_DIR=cx_build/$(ls cx_build)
mv $OUTPUT_DIR/lib/VERSION $OUTPUT_DIR
mv $OUTPUT_DIR/lib/res $OUTPUT_DIR
mv $OUTPUT_DIR/lib/backend_private $OUTPUT_DIR

# move all to target_dir
mv $OUTPUT_DIR/* $TARGET_DIR

# put it together
mkdir -p dist
tar -cvzf dist/thonny-$VERSION.tar.gz -C build $VERSION_NAME