#!/bin/bash

OPENSSL_VERSION="1.0.2f"

wget http://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz
tar -xvzf openssl-$OPENSSL_VERSION.tar.gz

cd openssl-$OPENSSL_VERSION
./config shared --prefix=$PREFIX --openssldir=$PREFIX/openssl
make
make install
cd ..
