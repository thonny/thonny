#!/usr/bin/env bash

wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tar.xz
tar xf Python-3.5.0.tar.xz
cd Python-3.5.0

# compile and install Python
./configure --prefix=$PREFIX LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include"

make
make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
#$PREFIX/bin/python3.5 -m idlelib




