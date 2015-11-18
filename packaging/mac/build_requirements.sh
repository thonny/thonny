#!/usr/bin/env bash

export PREFIX=/Users/aivar/pythonny

rm -Rf $PREFIX
mkdir $PREFIX


MAIN_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

TEMP_BUILD_DIR=$MAIN_DIR/temp_build_dir
rm -rf $TEMP_BUILD_DIR
mkdir $TEMP_BUILD_DIR
cd $TEMP_BUILD_DIR

# NB! If you update xcode then first do:
# sudo xcodebuild -license


$MAIN_DIR/build_tcltk.sh
#$MAIN_DIR/build_python.sh
#$MAIN_DIR/build_tkhtml.sh
#$MAIN_DIR/build_clean.sh


cd $MAIN_DIR # back to original dir

    
