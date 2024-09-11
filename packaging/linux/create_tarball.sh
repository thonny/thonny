#!/bin/bash

set -e

PREFIX=$HOME/pythonny310

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# prepare working folder
rm -rf build
TARGET_DIR=build/thonny
mkdir -p $TARGET_DIR




# copy files
cp -r $PREFIX/* $TARGET_DIR
cp install.py $TARGET_DIR/install.py
cp install.sh $TARGET_DIR/install

mkdir -p $TARGET_DIR/templates
cp uninstall.sh $TARGET_DIR/templates
cp Thonny.desktop $TARGET_DIR/templates

export LD_LIBRARY_PATH=$TARGET_DIR/lib

# INSTALL DEPS ###################################

if [ `getconf LONG_BIT` = "32" ]
then
#    $TARGET_DIR/bin/python3.10 -s -m pip install setuptools-scm

    # newer cryptography versions can't be (easily?) built on Ubuntu 16.04
    $TARGET_DIR/bin/python3.10 -s -m pip install cryptography==3.2.*
fi

$TARGET_DIR/bin/python3.10 -s -m pip install wheel
$TARGET_DIR/bin/python3.10 -s -m pip install --no-binary mypy -r ../requirements-regular-bundle.txt
$TARGET_DIR/bin/python3.10 -s -m pip install distro
$TARGET_DIR/bin/python3.10 -s -m pip install certifi

VERSION=$(<../../thonny/VERSION)

# INSTALL THONNY ###################################
$TARGET_DIR/bin/python3.10 -s -m pip install --pre --no-cache-dir thonny==$VERSION
#$TARGET_DIR/bin/python3.10 -s -m pip install ../setuptools/thonny-4.0.0b3.dev0-py3-none-any.whl

ARCHITECTURE="$(uname -m)"
VERSION_NAME=thonny-$VERSION-$ARCHITECTURE 


# clean up unnecessary stuff
rm -rf $TARGET_DIR/share
rm -rf $TARGET_DIR/man
rm -rf $TARGET_DIR/openssl

find $TARGET_DIR -type f -name "*.a" -delete
find $TARGET_DIR -type f -name "*.pyo" -delete
find $TARGET_DIR -type f -name "*.pyc" -delete
find $TARGET_DIR -type d -name "__pycache__" -delete

rm -rf $TARGET_DIR/lib/tk8.6/demos


rm -rf $TARGET_DIR/lib/python3.10/test
rm -rf $TARGET_DIR/lib/python3.10/idlelib
rm -rf $TARGET_DIR/lib/python3.10/distutils/command/*.exe
#rm -rf $TARGET_DIR/lib/python3.10/config-3.10m
#rm -rf $TARGET_DIR/lib/python3.10/site-packages/pip*
#rm -rf $TARGET_DIR/lib/python3.10/site-packages/setuptools*

rm -rf $TARGET_DIR/lib/python3.10/site-packages/pylint/test
rm -rf $TARGET_DIR/lib/python3.10/site-packages/mypy/test


# clear most of the include folder ##################################################
#rm -rf $TARGET_DIR/include/lzma
#rm -rf $TARGET_DIR/include/*.h
#mv $TARGET_DIR/include/python3.10m/pyconfig.h $SCRIPT_DIR # pip needs this
#rm -rf $TARGET_DIR/include/python3.10m/*
#mv $SCRIPT_DIR/pyconfig.h $TARGET_DIR/include/python3.10m # put it back



# clear bin because its scripts have absolute paths #################################
mv $TARGET_DIR/bin/python3.10 $SCRIPT_DIR # save python exe
rm -rf $TARGET_DIR/bin/*
mv $SCRIPT_DIR/python3.10 $TARGET_DIR/bin/

# create other executables and links
# NB! check that pip.sh refers to correct executable!
cp ../pip.sh $TARGET_DIR/bin/pip3.10

# create new commands ###############################################################
cp thonny $TARGET_DIR/bin

# create links ###############################################################
cd $TARGET_DIR/bin
ln -s python3.10 python3
ln -s pip3.10 pip3
cd $SCRIPT_DIR

# copy the token signifying Thonny-private Python
cp thonny_python.ini $TARGET_DIR/bin 

# copy libffi6, which is not present in newer Linuxes ...
if [ `getconf LONG_BIT` = "32" ]
then
  LIBFFI=/usr/lib/i386-linux-gnu/libffi.so.6.0.4
else
  LIBFFI=/usr/lib/x86_64-linux-gnu/libffi.so.6.0.4
fi
# ... unless this script is run in a newer machine
if [ -f "$LIBFFI" ]; then
  cp $LIBFFI $TARGET_DIR/lib
  cd $TARGET_DIR/lib
  ln -s libffi.so.6.0.4 libffi.so.6
  cd $SCRIPT_DIR
fi


# copy licenses
cp ../../*LICENSE.txt $TARGET_DIR

# put it together
mkdir -p dist
tar -cvzf dist/${VERSION_NAME}.tar.gz -C build thonny

# XXL ###########################################################

# $TARGET_DIR/bin/python3.10 -s -m pip install --no-cache-dir -r ../requirements-xxl-bundle.txt
#
# find $TARGET_DIR -type f -name "*.pyo" -delete
# find $TARGET_DIR -type f -name "*.pyc" -delete
#
# mkdir -p dist
# tar -cvzf dist/$XXL_VERSION_NAME.tar.gz -C build thonny
#
#
# create download + install script
# normal
DOWNINSTALL_FILENAME=thonny-${VERSION}.bash
DOWNINSTALL_TARGET=dist/$DOWNINSTALL_FILENAME
cp downinstall_template.sh $DOWNINSTALL_TARGET
sed -i "s/_VERSION_/${VERSION}/g" $DOWNINSTALL_TARGET
sed -i "s/_VARIANT_/thonny/g" $DOWNINSTALL_TARGET
#sed -i "s/_DEPS_/$(tr '\n' ' ' < ../requirements-regular-bundle.txt)/g" $DOWNINSTALL_TARGET
./insert_deps.py ../requirements-regular-bundle.txt $DOWNINSTALL_TARGET

# xxl
#XXL_DOWNINSTALL_FILENAME=thonny-xxl-$VERSION.bash
#XXL_DOWNINSTALL_TARGET=dist/$XXL_DOWNINSTALL_FILENAME
#cp downinstall_template.sh $XXL_DOWNINSTALL_TARGET
#sed -i "s/_VERSION_/$VERSION/g" $XXL_DOWNINSTALL_TARGET
#sed -i "s/_VARIANT_/thonny-xxl/g" $XXL_DOWNINSTALL_TARGET
#sed -i "s/_DEPS_/$(tr '\n' ' ' < ../requirements-xxl-bundle.txt)/g" $XXL_DOWNINSTALL_TARGET

