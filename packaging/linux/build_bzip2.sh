#!/bin/bash

set -e

BZIP2_VERSION=1.0.8
# https://lwn.net/Articles/762264/
# wget http://www.bzip.org/1.0.6/bzip2-$BZIP2_VERSION.tar.gz
wget https://fossies.org/linux/misc/bzip2-$BZIP2_VERSION.tar.gz
tar -xzf bzip2-$BZIP2_VERSION.tar.gz
cd bzip2-$BZIP2_VERSION
make -f Makefile-libbz2_so

mkdir -p $PREFIX/lib

cp -P libbz2.so.* $PREFIX/lib

cd ..
