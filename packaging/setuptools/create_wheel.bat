@echo ............... CHANGING TO PROJECT ROOT ......................
cd ..\..

@echo ............... CREATING wheel ................................

C:\Python36\python.exe setup.py bdist_wheel -d packaging\setuptools

cd packaging\setuptools
pause