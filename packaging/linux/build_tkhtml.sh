#!/usr/bin/env bash

# COMPILE TkHtml #####################################################
git clone https://github.com/olebole/tkhtml3.git

cd tkhtml3

# Generate some source files (see readme in https://github.com/starseeker/tcltk/tree/master/tkhtml)
$PREFIX/bin/tclsh8.6 src/cssprop.tcl
$PREFIX/bin/tclsh8.6 src/tokenlist.txt
$PREFIX/bin/tclsh8.6 src/mkdefaultstyle.tcl > htmldefaultstyle.c

# copy these generated files to src
mv *.c src
mv *.h src

# create build dir
mkdir build
cd build

# configure, make and install
chmod 755 ../configure
../configure \
	--prefix=$PREFIX \
	--with-tcl=$PREFIX/lib \
	--with-tk=$PREFIX/lib \
	--with-tclinclude=$PREFIX/include \
	--with-tkinclude=$PREFIX/include

make install
cd .. # back to tkhtml dir
cd .. # back to temp_build_dir


