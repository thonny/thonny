set PATH=C:\Python310-64\Scripts;%PATH%
@echo ............... CHANGING TO PROJECT ROOT ......................
cd ..\..

rmdir build /s /q

@echo ............... CREATING wheel ................................
python setup.py bdist_wheel -d packaging\setuptools

@echo ............... CREATING sdist ................................
python setup.py sdist --formats=gztar -d packaging\setuptools

cd packaging\setuptools

rmdir ..\..\thonny.egg-info /s /q

pause