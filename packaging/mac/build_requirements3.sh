#!/usr/bin/env bash

# This version takes official Python installation as base

export REGULAR_USER=$(whoami)
export PREFIX=$HOME/pythonny3
export RELATIVE_LIBDIR=@executable_path/../lib
MAIN_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
export TEMP_BUILD_DIR=$MAIN_DIR/temp_build_dir




rm -rf $TEMP_BUILD_DIR
mkdir $TEMP_BUILD_DIR
cd $TEMP_BUILD_DIR

# NB! If you update xcode then first do:
# sudo xcodebuild -license

rm -rf $PREFIX
mkdir $PREFIX

$MAIN_DIR/copy_python3.sh
cd $TEMP_BUILD_DIR


cd $MAIN_DIR


    
