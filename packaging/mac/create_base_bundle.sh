#!/usr/bin/env bash

# Should be run once per new version of Python or Tk

# Before running this
# * Install Python (official dmg)
# * Build and install Tcl/Tk (from source (install_tcltk.sh), because ActiveTcl licence is not compatible)
# * Build and install Pygame dependencies (SDL 1.2, libpng, and libjpeg))

# This version takes official Python installation as base

export PREFIX=$HOME/thonny_template_build
APP_TEMPLATE=$PREFIX/Thonny.app
export LOCAL_FRAMEWORKS=$APP_TEMPLATE/Contents/Frameworks

rm -rf $PREFIX
mkdir -p $PREFIX
cp -R -H Thonny.app.initial_template $APP_TEMPLATE

MAIN_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

$MAIN_DIR/copy_tcltk_frameworks.sh
$MAIN_DIR/copy_python_framework.sh
$MAIN_DIR/replace_tkinter.sh

$MAIN_DIR/copy_sdl_frameworks.sh
$MAIN_DIR/install_pygame.sh


    
