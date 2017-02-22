@echo ............... CHANGING TO PROJECT ROOT ......................
cd ..\..

@echo ............... CREATING BACKEND_PRIVATE ......................

mkdir thonny\backend_private
copy thonny_backend.py thonny\backend_private

mkdir thonny\backend_private\thonny
echo # Package marker> thonny\backend_private\thonny\__init__.py

copy thonny\backend.py    thonny\backend_private\thonny
copy thonny\misc_utils.py thonny\backend_private\thonny
copy thonny\ast_utils.py  thonny\backend_private\thonny
copy thonny\common.py     thonny\backend_private\thonny
 


@echo ............... CREATING wheel ................................

C:\Python36\python.exe setup.py bdist_wheel -d packaging\setuptools

@echo ............... CLEANING BACKEND_PRIVATE ......................

rmdir thonny\backend_private /s /q

cd packaging\setuptools
pause