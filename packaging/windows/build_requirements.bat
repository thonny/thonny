set PREFIX=pythonny

@echo ............... CLEANING ............................
rmdir %PREFIX% /S /Q
mkdir %PREFIX%

@echo ............... COPYING PYTHON ............................
xcopy C:\Python35\* %PREFIX% /S /E /K>NUL

@echo ............... INSTALLING JEDI ...................................
%PREFIX%\python.exe -m pip install --no-cache-dir jedi


pause
