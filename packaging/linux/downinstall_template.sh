#!/usr/bin/env bash
set -e

VER=VERSION 

echo 
echo "This script will download and install Thonny $VER for Linux (32 or 64-bit PC)."
read -p "Press ENTER to continue or Ctrl+C to cancel."

ARCHITECTURE="$(uname -m)"
FILENAME=thonny-$VER-$ARCHITECTURE.tar.gz
URL="https://github.com/thonny/thonny/releases/download/v$VER/$FILENAME"

echo "Downloading $URL"

wget -O $FILENAME $URL
tar -zxf $FILENAME
./thonny/install
rm -rf ./thonny
rm $FILENAME

echo 
read -p "Press ENTER to exit the installer."
