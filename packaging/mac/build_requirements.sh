#!/usr/bin/env bash

export REGULAR_USER=aivar
export PREFIX=/Users/$REGULAR_USER/pythonny
export RELATIVE_LIBDIR=@executable_path/../lib
MAIN_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
export TEMP_BUILD_DIR=$MAIN_DIR/temp_build_dir




rm -rf $TEMP_BUILD_DIR
mkdir $TEMP_BUILD_DIR
cd $TEMP_BUILD_DIR

# NB! If you update xcode then first do:
# sudo xcodebuild -license

#rm -Rf $PREFIX
#mkdir $PREFIX


#$MAIN_DIR/build_tcltk.sh
#$MAIN_DIR/build_tkhtml.sh
#$MAIN_DIR/build_python.sh
#$MAIN_DIR/copy_libraries.sh
#$MAIN_DIR/update_python_links.sh
$MAIN_DIR/clean_python.sh



cd $MAIN_DIR


    
