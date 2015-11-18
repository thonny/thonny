#!/usr/bin/env bash

export PREFIX=/Users/aivar/pythonny

rm -Rf $PREFIX
mkdir $PREFIX

rm -Rf ./temp_build_dir
mkdir ./temp_build_dir
cd temp_build_dir

# NB! If you update xcode then first do:
# sudo xcodebuild -license


./build_tcltk.sh
#./build_python.sh
#./build_tkhtml.sh
#./build_clean.sh


cd .. # back to original dir

    
