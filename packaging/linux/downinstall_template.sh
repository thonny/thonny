#!/usr/bin/env bash
set -e

echo "This script will download and install Thonny $VERSION for Linux."
read -p "Press ENTER to continue or Ctrl+C to cancel."
echo "Downloading Thonny ..."

ARCHITECTURE="$(uname -m)"
FILENAME=thonny-$VERSION-$ARCHITECTURE.tar.gz
URL="https://bitbucket.org/plas/thonny/downloads/$FILENAME"

wget $URL
tar -zxf $FILENAME
./thonny/install
rm -rf ./thonny
rm $FILENAME

read -p "Press ENTER to exit the installer."