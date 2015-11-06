set BUILDDIR=build

@echo ............... CLEANING ............................
rmdir %BUILDDIR% /S /Q
mkdir %BUILDDIR%

@echo ............... COPYING PYTHON ............................
xcopy C:\Python35\* %BUILDDIR% /S /E /K>NUL

@echo ............... CLEANING PYTHON ............................
cd %BUILDDIR%
move LICENSE.txt PYTHON-LICENSE.txt
del README.txt
del NEWS.txt
del test.bat
del /S *.pyc
del /S *.lib
del /S *.a
del /S *.chm
pause
rmdir Doc /S /Q
rmdir include /S /Q
rmdir libs /S /Q
rmdir Tools /S /Q

rmdir lib\test /S /Q
rmdir lib\plat-* /S /Q


rmdir tcl\tcl8 /S /Q
del tcl\*.sh /Q
del tcl\tcl8.6\clock.tcl
del tcl\tcl8.6\safe.tcl
rmdir tcl\tix8.4.3\demos /S /Q

rmdir tcl\tk8.6\demos /S /Q
rmdir tcl\tk8.6\msgs /S /Q

rmdir tcl\tcl8.6\opt0.4 /S /Q
rmdir tcl\tcl8.6\msgs /S /Q
rmdir tcl\tcl8.6\tzdata /S /Q
cd ..

@echo ............... COPYING THONNY ............................
copy ThonnyRunner\Release\thonny.exe
copy ..\..\*.py %BUILDDIR%
copy ..\..\VERSION %BUILDDIR%
xcopy ..\..\thonny %BUILDDIR% /S /E /K>NUL
xcopy ..\..\rope %BUILDDIR% /S /E /K>NUL
xcopy ..\..\jedi %BUILDDIR% /S /E /K>NUL

