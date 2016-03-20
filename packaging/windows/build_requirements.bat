set PREFIX=pythonny

@echo ............... CLEANING ............................
rmdir %PREFIX% /S /Q
mkdir %PREFIX%

@echo ............... COPYING PYTHON ............................
xcopy C:\Python35\* %PREFIX% /S /E /K>NUL

@echo ............... INSTALLING JEDI ...................................
%PREFIX%\python.exe -m pip install --no-cache-dir jedi

@echo ............... INSTALLING NUMPY ...................................
%PREFIX%\python.exe -m pip install --no-cache-dir numpy

@echo ............... INSTALLING PYGAME ...................................
bitsadmin /transfer myDownloadJob /download /priority normal http://www.lfd.uci.edu/~gohlke/pythonlibs/djcobkfp/pygame-1.9.2a0-cp35-none-win32.whl .\pygame-1.9.2a0-cp35-none-win32.whl
%PREFIX%\python.exe -m pip install --no-cache-dir pygame-1.9.2a0-cp35-none-win32.whl


pause
