#!/usr/bin/env bash


git clone https://github.com/petasis/tkdnd.git

cd tkdnd


# configure, make and install
chmod 755 ../configure
../configure \
	--prefix=$PREFIX \
	--with-tcl=$PREFIX/lib \
	--with-tk=$PREFIX/lib \
	--with-tclinclude=$PREFIX/include \
	--with-tkinclude=$PREFIX/include \
        --without-x

make install



