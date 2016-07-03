#!/bin/bash

# Copied from http://pygame.org/wiki/MacCompile

# Install the SDL libraries from dmg (http://www.libsdl.org/) 
# SDL 1.2.15
# SDL_mixer 1.2.12
# SDL_ttf 2.0.11
# SDL_image 1.2.12

# Before compilation of pygame:
# SDL_x header files refer to SDL as <SDL/SDL_yy.h> However, a SDL directory is not under the 
# include directory of SDL (SDL/Headers). To fix this in a simple way: Went to directory 
# /Library/Frameworks/SDL.framework/Headers then made a link as follows ln -s 
# SDL ./ (Didn't work for me, made dir and copied).

# Install the libjpeg and libpng libraries from dmg (http://ethan.tira-thompson.com/Mac_OS_X_Ports.html)

# Install XQuartz. Mountain Lion OS X no longer includes the X11 window system library. This is different from Lion OS X (http://xquartz.macosforge.org/landing/)

INITIAL_DIR=$(pwd)
TEMP_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/temp_build_dir
LOCAL_FRAMEWORKS=$HOME/thonny_template_build/Thonny.app/Contents/Frameworks

cd $TEMP_DIR
rm -rf $TEMP_DIR/pygame

# Get Pygame
hg clone https://bitbucket.org/pygame/pygame

# Compile Pygame
cd pygame

export CC='/usr/bin/gcc' 
export MACOSX_DEPLOYMENT_TARGET=10.6
export CFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -I/opt/X11/include"
export LDFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6"
export CXXFLAGS="$CFLAGS"
export ARCHFLAGS="-arch i386 -arch x86_64"


PYTHON_EXE=$LOCAL_FRAMEWORKS/Python.framework/Versions/3.5/bin/python3.5
$PYTHON_EXE config.py         # This should find the SDL, jpeg, png, and numpy libraries.
$PYTHON_EXE setup.py build    # This will build in the directory before installing. It should complete with no errors.
$PYTHON_EXE setup.py install  

# add numpy
#$PYTHON_EXE -m pip install numpy

# add libpng and libjpg and relink imageext
cp /usr/local/lib/libjpeg.8.dylib $LOCAL_FRAMEWORKS
cp /opt/X11/lib/libpng15.15.dylib $LOCAL_FRAMEWORKS

install_name_tool -change \
    /usr/local/lib/libjpeg.8.dylib \
	@rpath/libjpeg.8.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.5/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

install_name_tool -change \
    /opt/X11/lib/libpng15.15.dylib \
	@rpath/libpng15.15.dylib \
	$LOCAL_FRAMEWORKS/Python.framework/Versions/3.5/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

cd $INITIAL_DIR