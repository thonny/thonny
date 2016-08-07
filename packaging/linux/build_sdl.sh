#!/bin/bash

set -e

PREFIX=$HOME/pyg
export LD_LIBRARY_PATH=$PREFIX/lib

rm -rf $PREFIX
mkdir -p $PREFIX

TEMP="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/pygbuild"
rm -rf $TEMP
mkdir -p $TEMP
cd $TEMP


# zlib ------------------------------------------
cd $TEMP
ZLIB_VER=1.2.8
wget http://zlib.net/zlib-$ZLIB_VER.tar.gz
tar -xzf zlib-$ZLIB_VER.tar.gz
cd zlib-$ZLIB_VER
./configure --prefix=$PREFIX
make install

# libpng ----------------------------------------
cd $TEMP
LIBPNG_VER=1.6.24
wget ftp://ftp.simplesystems.org/pub/libpng/png/src/libpng16/libpng-$LIBPNG_VER.tar.gz
tar -xzf libpng-$LIBPNG_VER.tar.gz
cd libpng-$LIBPNG_VER
./configure --prefix=$PREFIX
make install

# jpeg --------------------------------------------
#cd $TEMP
#JPEG_VER=1.4.2
#wget https://sourceforge.net/projects/libjpeg-turbo/files/$JPEG_VER/libjpeg-turbo-$JPEG_VER.tar.gz/download -O libjpeg-turbo-$JPEG_VER.tar.gz
#tar -xzf libjpeg-turbo-$JPEG_VER.tar.gz
#cd libjpeg-turbo-$JPEG_VER
#./configure --prefix=$PREFIX --with-jpeg8
#make install

# webp --------------------------------------------
#cd $TEMP
#WEBP_VER=0.5.1
#wget http://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-$WEBP_VER.tar.gz
#tar -xzf libwebp-$WEBP_VER.tar.gz
#cd libwebp-$WEBP_VER
#./configure --prefix=$PREFIX
#make install

# sdl ---------------------------------------------------
cd $TEMP
SDL_VER=1.2.15
wget https://www.libsdl.org/release/SDL-$SDL_VER.tar.gz
tar -xzf SDL-$SDL_VER.tar.gz
cd SDL-$SDL_VER
./configure --prefix=$PREFIX
make install

# smpeg -------------------------------------------------
# https://searchcode.com/codesearch/view/65821733/

cd $TEMP
svn co svn://svn.icculus.org/smpeg/tags/release_0_4_5/ smpeg
cd smpeg
./autogen.sh
./configure --prefix=$PREFIX \
	--disable-debug \
	--disable-dependency-tracking \
    --disable-gtktest \
    --disable-sdltest
make install

# sdl_image ---------------------------------------------------
cd $TEMP
IMAGE_VER=1.2.12
wget https://www.libsdl.org/projects/SDL_image/release/SDL_image-$IMAGE_VER.tar.gz
tar -xzf SDL_image-$IMAGE_VER.tar.gz
cd SDL_image-$IMAGE_VER
./configure --prefix=$PREFIX
make install

# sdl_mixer ---------------------------------------------------
cd $TEMP
MIXER_VER=1.2.12
wget https://www.libsdl.org/projects/SDL_mixer/release/SDL_mixer-$MIXER_VER.tar.gz
tar -xzf SDL_mixer-$MIXER_VER.tar.gz
cd SDL_mixer-$MIXER_VER
./configure --prefix=$PREFIX
make install

# sdl_ttf ---------------------------------------------------
cd $TEMP
TTF_VER=2.0.11
wget https://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-$TTF_VER.tar.gz
tar -xzf SDL_ttf-$TTF_VER.tar.gz
cd SDL_ttf-$TTF_VER
./configure --prefix=$PREFIX
make install

