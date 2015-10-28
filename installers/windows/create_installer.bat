@echo off
set FREEZE_TARGET=cx_build\exe.win32-3.5

@echo ............... CLEANING ............................
rmdir cx_build /s /q


REM following two variables are fix for a bug in cx_freeze in Python 3.5
set TCL_LIBRARY=C:\Python35\tcl\tcl8.6
set TK_LIBRARY=C:\Python35\tcl\tk8.6

@echo ............... FREEZING ............................
C:\python35\python ..\cx_freeze\setup.py build -b cx_build > freezing.log

@echo ............... COPYING DLLs ........................
copy c:\python35\DLLs\*.dll %FREEZE_TARGET%

@echo ............... ENABLING DPI AWARENESS ..............
call EnableDPIAwareness %FREEZE_TARGET%\thonny_frontend.exe
call EnableDPIAwareness %FREEZE_TARGET%\thonny_backend.exe

@echo ............... BUILDING INSTALLER ..................
set /p VERSION=<..\..\VERSION
"C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=%VERSION% /dSourceFolder=%FREEZE_TARGET% inno_setup.iss > installer_building.log


@echo ............... DONE! ...............................
pause

