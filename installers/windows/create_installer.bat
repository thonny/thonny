set FREEZE_TARGET=cx_build\exe.win32-3.4

@echo ............... CLEANING .................
rmdir build /s /q


REM following two variables are fix for a bug in cx_freeze in Python 3.5
REM set TCL_LIBRARY=C:\Program Files (x86)\Python 3.5\tcl\tcl8.6
REM set TK_LIBRARY=C:\Program Files (x86)\Python 3.5\tcl\tk8.6
@echo ............... FREEZING ...............
C:\python34\python ..\cx_freeze\setup.py build -b cx_build > freezing.log

@echo ............... DISABLING DPI AWARENESS ...............
call DisableDPIAwareness %FREEZE_TARGET%\thonny_frontend.exe
call DisableDPIAwareness %FREEZE_TARGET%\thonny_backend.exe

@echo ............... BUILDING INSTALLER ...............
set /p VERSION=<..\..\thonny\VERSION
"C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=%VERSION% /dSourceFolder=%FREEZE_TARGET% inno_setup.iss > installer_building.log
pause

