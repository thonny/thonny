#!/usr/bin/env bash

# START BUILDING ####################################################
PREFIX=/home/aivar/pythonny

rm -Rf $PREFIX
mkdir $PREFIX


rm -Rf ./temp_build_dir
mkdir ./temp_build_dir
cd temp_build_dir

# COMPILE TCL/TK ####################################################
wget http://prdownloads.sourceforge.net/tcl/tcl8.6.4-src.tar.gz
tar -xzf tcl8.6.4-src.tar.gz
cd tcl8.6.4/unix
./configure --prefix=$PREFIX
make install
cd ../..

wget http://prdownloads.sourceforge.net/tcl/tk8.6.4-src.tar.gz
tar -xzf tk8.6.4-src.tar.gz
cd tk8.6.4/unix
# see http://sourceforge.net/p/tktoolkit/bugs/2588/ for --disable-xss
./configure --prefix=$PREFIX --disable-xss 
make install
cd ../..

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


# INSTALL PYTHON ###############################################

wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tar.xz
tar xf Python-3.5.0.tar.xz
cd Python-3.5.0

# set LD_LIBRARY_PATH (https://mail.python.org/pipermail/tkinter-discuss/2011-March/002808.html)
export LD_LIBRARY_PATH=$PREFIX/lib

# compile and install Python
./configure \
	--prefix=$PREFIX \
	--with-tcltk-includes=-I$PREFIX/include \
	--with-tcltk-libs=-L$PREFIX/lib

make altinstall

# check that the newly built Python uses Tk 8.6 for Tkinter
$PREFIX/bin/python3.5 -m idlelib

# CLEAN PYTHON ###########################################
rm -rf $PREFIX/share
# rm -rf $PREFIX/include # TODO: pyconfig.h is required by pip
rm -rf $PREFIX/man
rm $PREFIX/bin/2to3-3.5
rm $PREFIX/bin/easy_install-3.5
rm $PREFIX/bin/idle3.5
rm $PREFIX/bin/pip3.5
rm $PREFIX/bin/pydoc3.5
rm $PREFIX/bin/python3.5m
rm $PREFIX/bin/python3.5m-config
rm $PREFIX/bin/pyvenv-3.5
rm $PREFIX/bin/tclsh8.6
rm $PREFIX/bin/wish8.6

rm -f $PREFIX/lib/libpython3.5m.a

rm -rf $PREFIX/lib/python3.5/__pycache__
# rm -rf $PREFIX/lib/python3.5/config-3.5m # TODO: makefile is required
rm -rf $PREFIX/lib/python3.5/test

find $PREFIX/lib -name '*.pyc' -delete
find $PREFIX/lib -name '*.exe' -delete

##########################################################
# back to original dir
cd ..
