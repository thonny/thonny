cd ../..
rm -rf build
python3 setup.py bdist_wheel -d packaging/setuptools
python3 setup.py sdist --formats=gztar -d packaging/setuptools
cd packaging/setuptools

