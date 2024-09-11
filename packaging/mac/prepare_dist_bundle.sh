#!/bin/bash
set -e

VERSION=$1
shift
req_files="$@"

PREFIX=$HOME/thonny_template_build_310
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# prepare working folder #########################################################
rm -rf build
mkdir -p build


# copy template #################################################
cp -R -H $PREFIX/Thonny.app build

chmod 644  build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.10/lib/libtcl8.6.dylib
chmod 644 build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.10/lib/libtk8.6.dylib

# update template (might have changed after last create_base_bundle.sh) #####################
cp $SCRIPT_DIR/Thonny.app.initial_template/Contents/MacOS/* \
    build/Thonny.app/Contents/MacOS
cp $SCRIPT_DIR/Thonny.app.initial_template/Contents/Resources/* \
    build/Thonny.app/Contents/Resources
cp $SCRIPT_DIR/Thonny.app.initial_template/Contents/Info.plist \
    build/Thonny.app/Contents

FRAMEWORKS=build/Thonny.app/Contents/Frameworks
PYTHON_CURRENT=$FRAMEWORKS/Python.framework/Versions/3.10

# install #####################################################
export MACOSX_DEPLOYMENT_TARGET=10.9
export SDKROOT=~/MacOSX10.9.sdk

$PYTHON_CURRENT/bin/python3.10 -s -m pip install --no-cache-dir wheel

# Force Universal2 builds for certain deps, which would come single arch otherwise
$PYTHON_CURRENT/bin/python3.10 -s -m pip install universal_dists/bitarray-2.9.2-cp310-cp310-macosx_10_9_universal2.whl
$PYTHON_CURRENT/bin/python3.10 -s -m pip install universal_dists/cffi-1.17.1-cp310-cp310-macosx_10_9_universal2.whl
$PYTHON_CURRENT/bin/python3.10 -s -m pip install universal_dists/PyYAML-6.0.2-cp310-cp310-macosx_10_9_universal2.whl
$PYTHON_CURRENT/bin/python3.10 -s -m pip install universal_dists/cryptography-38.0.4-cp36-abi3-macosx_10_10_universal2.whl
$PYTHON_CURRENT/bin/python3.10 -s -m pip install universal_dists/websockets-11.0.3-cp310-cp310-macosx_10_9_universal2.whl

for req_file in $req_files
do
	echo "installing from $req_file"
	$PYTHON_CURRENT/bin/python3.10  -s -m pip install --no-binary mypy --no-binary lxml -r $req_file
done
$PYTHON_CURRENT/bin/python3.10 -s -m pip install --no-cache-dir certifi
$PYTHON_CURRENT/bin/python3.10 -s -m pip install --pre --no-cache-dir "thonny==${VERSION}"
#$PYTHON_CURRENT/bin/python3.10 -s -m pip install ../setuptools/thonny-4.1.0b1.dev0-py3-none-any.whl

rm $PYTHON_CURRENT/bin/thonny # because Thonny is not supposed to run from there


# save some space ###################################################
rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.6/Tcl_debug
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.6/Tk_debug
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.6/Resources/Scripts/demos
rm -rf $FRAMEWORKS/Tcl.framework/Versions/8.6/Resources/Documentation
rm -rf $FRAMEWORKS/Tk.framework/Versions/8.6/Resources/Documentation

rm -rf $PYTHON_CURRENT/Resources/English.lproj/Documentation

rm -rf $PYTHON_CURRENT/share

rm -rf $PYTHON_CURRENT/lib/python3.10/test
rm -rf $PYTHON_CURRENT/lib/python3.10/distutils/test
rm -rf $PYTHON_CURRENT/lib/python3.10/lib2to3/test
rm -rf $PYTHON_CURRENT/lib/python3.10/unittest/test

rm -rf $PYTHON_CURRENT/lib/python3.10/idlelib
rm -rf $PYTHON_CURRENT/bin/idle3
rm -rf $PYTHON_CURRENT/bin/idle3.10

rm -rf $PYTHON_CURRENT/lib/python3.10/site-packages/pylint/test
rm -rf $PYTHON_CURRENT/lib/python3.10/site-packages/mypy/test

find $PYTHON_CURRENT/lib -name '*.pyc' -delete
find $PYTHON_CURRENT/lib -name '*.exe' -delete

# for some reason the notarizer doesn't like txt files in these packages
find $PYTHON_CURRENT/lib/python3.10/site-packages/lxml -name '*.txt' -delete       || true
find $PYTHON_CURRENT/lib/python3.10/site-packages/matplotlib -name '*.txt' -delete || true


# create link to Python.app interpreter
cd build/Thonny.app/Contents/MacOS
ln -s ../Frameworks/Python.framework/Versions/3.10/Resources/Python.app/Contents/MacOS/Python Python
cd $SCRIPT_DIR


# copy the token signifying Thonny-private Python
cp thonny_python.ini $PYTHON_CURRENT/bin 

./make_scripts_relocatable.py "$PYTHON_CURRENT/bin" 




# set version info ##############################################################
sed -i '' "s/VERSION/$VERSION/" build/Thonny.app/Contents/Info.plist



