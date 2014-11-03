#!/bin/bash

# prepare working folder
rm -rf build
mkdir -p build

# copy template and source files
cp -r Thonny.app.template build/Thonny.app
#mv build/Thonny.app.template build/Thonny.app
cp -r ../thonny build/Thonny.app/Contents/MacOS
chmod 755 build/Thonny.app/Contents/MacOS/thonny_launch

# clean up unnecessary stuff
rm -rf build/Thonny.app/Contents/MacOs/thonny/__pycache__
rm -rf build/Thonny.app/Contents/MacOs/thonny/*.pyo
rm -rf build/Thonny.app/Contents/MacOs/thonny/*.pyc 

# get and set version
VERSION=$(<../thonny/VERSION)
sed -i.bak "s/VERSION/$VERSION/" build/Thonny.app/Contents/Info.plist
rm -f build/Thonny.app/Contents/Info.plist.bak


# create dmg
mkdir -p dist
FILENAME=dist/thonny-$VERSION.dmg
rm -f $FILENAME
hdiutil create -srcfolder build/Thonny.app $FILENAME
hdiutil internet-enable -yes $FILENAME

