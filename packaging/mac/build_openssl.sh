#!/bin/bash

OPENSSL_VERSION="1.0.2e"

curl -O http://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz
tar -xvzf openssl-$OPENSSL_VERSION.tar.gz

cd openssl-$OPENSSL_VERSION
./Configure --prefix=$PREFIX darwin64-x86_64-cc -shared
make
make install
cd ..