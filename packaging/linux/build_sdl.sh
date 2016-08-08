#!/bin/bash

set -e

#PREFIX=$HOME/pyg
#export LD_LIBRARY_PATH=$PREFIX/lib
export CPPFLAGS=-I$PREFIX/include
export LDFLAGS=-L$PREFIX/lib

#rm -rf $PREFIX
#mkdir -p $PREFIX

#TEMP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/pygbuild"
#rm -rf $TEMP_DIR
#mkdir -p $TEMP_DIR
cd $TEMP_DIR


# sdl ---------------------------------------------------
cd $TEMP_DIR
SDL_VER=1.2.15
wget https://www.libsdl.org/release/SDL-$SDL_VER.tar.gz
tar -xzf SDL-$SDL_VER.tar.gz
cd SDL-$SDL_VER
./configure --prefix=$PREFIX
make install


# zlib ------------------------------------------
cd $TEMP_DIR
ZLIB_VER=1.2.8
wget http://zlib.net/zlib-$ZLIB_VER.tar.gz
tar -xzf zlib-$ZLIB_VER.tar.gz
cd zlib-$ZLIB_VER
./configure --prefix=$PREFIX
make install

# libpng ----------------------------------------
cd $TEMP_DIR
LIBPNG_VER=1.6.24
wget ftp://ftp.simplesystems.org/pub/libpng/png/src/libpng16/libpng-$LIBPNG_VER.tar.gz
tar -xzf libpng-$LIBPNG_VER.tar.gz
cd libpng-$LIBPNG_VER
./configure --prefix=$PREFIX
make install

# jpeg --------------------------------------------
cd $TEMP_DIR
JPEG_VER=1.4.2
wget https://sourceforge.net/projects/libjpeg-turbo/files/$JPEG_VER/libjpeg-turbo-$JPEG_VER.tar.gz/download -O libjpeg-turbo-$JPEG_VER.tar.gz
tar -xzf libjpeg-turbo-$JPEG_VER.tar.gz
cd libjpeg-turbo-$JPEG_VER
./configure --prefix=$PREFIX --with-jpeg8
make install

# webp --------------------------------------------
cd $TEMP_DIR
WEBP_VER=0.5.1
wget http://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-$WEBP_VER.tar.gz
tar -xzf libwebp-$WEBP_VER.tar.gz
cd libwebp-$WEBP_VER
./configure --prefix=$PREFIX
make install

# sdl_image ---------------------------------------------------
cd $TEMP_DIR
IMAGE_VER=1.2.12
wget https://www.libsdl.org/projects/SDL_image/release/SDL_image-$IMAGE_VER.tar.gz
tar -xzf SDL_image-$IMAGE_VER.tar.gz
cd SDL_image-$IMAGE_VER
./configure --prefix=$PREFIX
make install

# ogg --------------------------------------------
cd $TEMP_DIR
OGG_VER=1.3.2
wget http://downloads.xiph.org/releases/ogg/libogg-$OGG_VER.tar.gz
tar -xzf libogg-$OGG_VER.tar.gz
cd libogg-$OGG_VER
./configure --prefix=$PREFIX
make install

# vorbis --------------------------------------------
cd $TEMP_DIR
VORBIS_VER=1.3.5
wget http://downloads.xiph.org/releases/vorbis/libvorbis-$VORBIS_VER.tar.gz
tar -xzf libvorbis-$VORBIS_VER.tar.gz
cd libvorbis-$VORBIS_VER
./configure --prefix=$PREFIX
make install

# mikmod --------------------------------------------
cd $TEMP_DIR
MIKMOD_VER=3.3.8
wget https://sourceforge.net/projects/mikmod/files/libmikmod/$MIKMOD_VER/libmikmod-$MIKMOD_VER.tar.gz/download -O libmikmod-$MIKMOD_VER.tar.gz
tar -xzf libmikmod-$MIKMOD_VER.tar.gz
cd libmikmod-$MIKMOD_VER
./configure --prefix=$PREFIX
make install

# smpeg -------------------------------------------------
# https://searchcode.com/codesearch/view/65821733/

cd $TEMP_DIR
svn co svn://svn.icculus.org/smpeg/tags/release_0_4_5/ smpeg
cd smpeg
./autogen.sh
./configure --prefix=$PREFIX \
	--disable-debug \
	--disable-dependency-tracking \
    --disable-gtktest \
    --disable-sdltest
make install

# sdl_mixer ---------------------------------------------------
cd $TEMP_DIR
MIXER_VER=1.2.12
wget https://www.libsdl.org/projects/SDL_mixer/release/SDL_mixer-$MIXER_VER.tar.gz
tar -xzf SDL_mixer-$MIXER_VER.tar.gz
cd SDL_mixer-$MIXER_VER
./configure --prefix=$PREFIX
make install

# sdl_ttf ---------------------------------------------------
cd $TEMP_DIR
TTF_VER=2.0.11
wget https://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-$TTF_VER.tar.gz
tar -xzf SDL_ttf-$TTF_VER.tar.gz
cd SDL_ttf-$TTF_VER
./configure --prefix=$PREFIX
make install

