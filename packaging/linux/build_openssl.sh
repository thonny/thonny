#!/bin/bash

set -e

OPENSSL_VERSION="1.1.1j"

wget http://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz
tar -xvzf openssl-$OPENSSL_VERSION.tar.gz

cd openssl-$OPENSSL_VERSION
./config shared --prefix=$PREFIX --openssldir=$PREFIX/openssl
make
make install
cd ..
