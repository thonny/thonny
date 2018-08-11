#!/usr/bin/env bash

set -e

# START BUILDING ####################################################
export PREFIX=$HOME/pythonny37

export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt 
export LD_LIBRARY_PATH=$PREFIX/lib

ARCHITECTURE="$(uname -m)"

rm -Rf $PREFIX
mkdir $PREFIX
MAIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

TEMP_DIR=$MAIN_DIR/temp_build_dir
rm -Rf $TEMP_DIR
mkdir $TEMP_DIR
cd $TEMP_DIR


$MAIN_DIR/build_bzip2.sh
$MAIN_DIR/build_xz.sh
$MAIN_DIR/build_tcltk.sh
$MAIN_DIR/build_openssl.sh
$MAIN_DIR/build_python.sh

# COPY SOME LIBS #########################################
# using star because this script must work both in 32 and 64-bit Ubuntu
#cp /lib/*-linux-gnu/libbz2.so.1.0.4 $PREFIX/lib/libbz2.so.1.0

##########################################################
# back to original dir
cd ..

# check it out ...
$PREFIX/bin/python3.7 -m idlelib
