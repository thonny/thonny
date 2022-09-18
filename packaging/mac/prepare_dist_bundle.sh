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

for req_file in $req_files
do
	echo "installing from $req_file"
	$PYTHON_CURRENT/bin/python3.10  -s -m pip install --no-binary mypy --no-binary lxml -r $req_file
done
$PYTHON_CURRENT/bin/python3.10 -s -m pip install --no-cache-dir certifi
$PYTHON_CURRENT/bin/python3.10 -s -m pip install --pre --no-cache-dir "thonny==${VERSION}"
#$PYTHON_CURRENT/bin/python3.10 -s -m pip install ../setuptools/thonny-4.0.0.dev1-py3-none-any.whl

rm $PYTHON_CURRENT/bin/thonny # because Thonny is not supposed to run from there

# make the packages more universal
# assuming $HOME/thonny_alt_packages/pkgs contains compatible universal2 version of cryptography
# and arm64 version of cffi
cp $HOME/thonny_alt_packages/pkgs/cryptography/hazmat/bindings/*.so \
  $PYTHON_CURRENT/lib/python3.10/site-packages/cryptography/hazmat/bindings

cp $HOME/thonny_alt_packages/pkgs/_cffi_backend.cpython-310-darwin.so \
  $PYTHON_CURRENT/lib/python3.10/site-packages/_cffi_backend.cpython-310-darwin-arm46.so



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



