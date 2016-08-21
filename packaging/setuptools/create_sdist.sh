#!/bin/bash

cd ../..
mkdir thonny/backend_private
cp thonny_backend.py thonny/backend_private

mkdir thonny/backend_private/thonny
echo "# Package marker" > thonny/backend_private/thonny/__init__.py

cp thonny/backend.py    thonny/backend_private/thonny
cp thonny/misc_utils.py thonny/backend_private/thonny
cp thonny/ast_utils.py  thonny/backend_private/thonny
cp thonny/common.py     thonny/backend_private/thonny
 
python3.5 setup.py sdist --formats=zip -d packaging/setuptools

rm -rf thonny/backend_private

cd packaging/setuptools
