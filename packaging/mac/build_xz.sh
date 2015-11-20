#!/bin/bash

XZ_VERSION=5.2.2

curl -O http://tukaani.org/xz/xz-$XZ_VERSION.tar.gz
tar -xvzf xz-$XZ_VERSION.tar.gz
cd xz-$XZ_VERSION
./configure --prefix=$PREFIX
make
make install

cd ..