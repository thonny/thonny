#!/bin/bash

PREFIX=$HOME/pyg
export LD_LIBRARY_PATH=$HOME/lib

#rm -rf $PREFIX
#mkdir -p $PREFIX

TEMP="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/pygbuild"
#rm -rf $TEMP
#mkdir -p $TEMP
cd $TEMP

# zlib ------------------------------------------
#cd $TEMP
#ZLIB_VER=1.2.8
#wget http://zlib.net/zlib-$ZLIB_VER.tar.gz
#tar -xzf zlib-$ZLIB_VER.tar.gz
#cd zlib-$ZLIB_VER
#./configure --prefix=$PREFIX
#make install

# libpng ----------------------------------------
#cd $TEMP
#LIBPNG_VER=1.6.23
#wget ftp://ftp.simplesystems.org/pub/libpng/png/src/libpng16/libpng-1.6.23.tar.gz
#tar -xzf libpng-$LIBPNG_VER.tar.gz
#cd libpng-$LIBPNG_VER
#./configure --prefix=$PREFIX
#make install

# jpeg --------------------------------------------
cd $TEMP
JPEG_VER=1.4.2
#wget https://sourceforge.net/projects/libjpeg-turbo/files/$JPEG_VER/libjpeg-turbo-$JPEG_VER.tar.gz/download -O libjpeg-turbo-$JPEG_VER.tar.gz
tar -xzf libjpeg-turbo-$JPEG_VER.tar.gz
cd libjpeg-turbo-$JPEG_VER
./configure --prefix=$PREFIX --with-jpeg8
make install

