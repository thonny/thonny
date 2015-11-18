#!/usr/bin/env bash

# START BUILDING ####################################################
PREFIX=/home/aivar/pythonny
ARCHITECTURE="$(uname -m)"

rm -Rf $PREFIX
mkdir $PREFIX

MAIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

TEMP_DIR=$MAIN_DIR/temp_build_dir
rm -Rf $TEMP_DIR
mkdir $TEMP_DIR
cd $TEMP_DIR

$MAIN_DIR/build_tcltk.sh
$MAIN_DIR/build_tkhtml.sh
$MAIN_DIR/build_python.sh



# COPY SOME LIBS #########################################
# using star because it must work both in 32 and 64-bit Ubuntu
cp /lib/*-linux-gnu/libbz2.so.1.0.4 $PREFIX/lib/libbz2.so.1.0
cp /lib/*-linux-gnu/libssl.so.1.0.0 $PREFIX/lib/libssl.so.1.0.0
cp /lib/*-linux-gnu/libcrypto.so.1.0.0 $PREFIX/lib/libcrypto.so.1.0.0

##########################################################
# back to original dir
cd ..
