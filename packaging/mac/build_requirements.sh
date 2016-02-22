#!/usr/bin/env bash

export REGULAR_USER=$(whoami)
export PREFIX=$HOME/pythonny
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


$MAIN_DIR/build_tcltk.sh 8.6
cd $TEMP_BUILD_DIR

#$MAIN_DIR/build_tkhtml.sh
#cd $TEMP_BUILD_DIR

$MAIN_DIR/build_openssl.sh
cd $TEMP_BUILD_DIR

$MAIN_DIR/build_xz.sh
cd $TEMP_BUILD_DIR

$MAIN_DIR/build_python.sh
cd $TEMP_BUILD_DIR

$MAIN_DIR/update_links.sh
cd $TEMP_BUILD_DIR


cd $MAIN_DIR


    
