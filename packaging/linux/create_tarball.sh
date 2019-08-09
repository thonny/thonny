#!/bin/bash

set -e

PREFIX=$HOME/pythonny37

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
    $TARGET_DIR/bin/python3.7 -m pip install setuptools-scm
fi

$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir asttokens==1.1.*
$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir parso==0.5.*
$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir jedi==0.14.*
$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir --no-binary mypy mypy==0.720
$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir pylint==2.3.*
$TARGET_DIR/bin/python3.7 -m pip install docutils==0.15.*
$TARGET_DIR/bin/python3.7 -m pip install pyserial==3.4
$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir distro==1.4.*
$TARGET_DIR/bin/python3.7 -m pip install --no-cache-dir certifi

# INSTALL THONNY ###################################
$TARGET_DIR/bin/python3.7 -m pip install --pre --no-cache-dir thonny

VERSION=$(<$TARGET_DIR/lib/python3.7/site-packages/thonny/VERSION)
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


rm -rf $TARGET_DIR/lib/python3.7/test
rm -rf $TARGET_DIR/lib/python3.7/idlelib
rm -rf $TARGET_DIR/lib/python3.7/distutils/command/*.exe
#rm -rf $TARGET_DIR/lib/python3.7/config-3.7m
#rm -rf $TARGET_DIR/lib/python3.7/site-packages/pip*
#rm -rf $TARGET_DIR/lib/python3.7/site-packages/setuptools*

rm -rf $TARGET_DIR/lib/python3.7/site-packages/pylint/test
rm -rf $TARGET_DIR/lib/python3.7/site-packages/mypy/test


# clear most of the include folder ##################################################
#rm -rf $TARGET_DIR/include/lzma
#rm -rf $TARGET_DIR/include/*.h
#mv $TARGET_DIR/include/python3.7m/pyconfig.h $SCRIPT_DIR # pip needs this
#rm -rf $TARGET_DIR/include/python3.7m/*
#mv $SCRIPT_DIR/pyconfig.h $TARGET_DIR/include/python3.7m # put it back



# clear bin because its scripts have absolute paths #################################
mv $TARGET_DIR/bin/python3.7 $SCRIPT_DIR # save python exe
rm -rf $TARGET_DIR/bin/*
mv $SCRIPT_DIR/python3.7 $TARGET_DIR/bin/

# create other executables and links
# NB! check that pip.sh refers to correct executable!
cp ../pip.sh $TARGET_DIR/bin/pip3.7

# create new commands ###############################################################
cp thonny $TARGET_DIR/bin

# create links ###############################################################
cd $TARGET_DIR/bin
ln -s python3.7 python3
ln -s pip3.7 pip3
cd $SCRIPT_DIR

# copy the token signifying Thonny-private Python
cp thonny_python.ini $TARGET_DIR/bin 




# copy licenses
cp ../../*LICENSE.txt $TARGET_DIR

# put it together
mkdir -p dist
tar -cvzf dist/$VERSION_NAME.tar.gz -C build thonny


# create download + install script
DOWNINSTALL_FILENAME=thonny-$VERSION.bash

DOWNINSTALL_TARGET=dist/$DOWNINSTALL_FILENAME
cp downinstall_template.sh $DOWNINSTALL_TARGET
sed -i "s/VERSION/$VERSION/g" $DOWNINSTALL_TARGET

