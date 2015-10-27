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
python3 ../cx_freeze/setup.py build -b cx_build > freezing.log

