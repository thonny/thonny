rmdir build /s /q

REM following two variables are fix for a bug in cx_freeze in Python 3.5
REM set TCL_LIBRARY=C:\Program Files (x86)\Python 3.5\tcl\tcl8.6
REM set TK_LIBRARY=C:\Program Files (x86)\Python 3.5\tcl\tk8.6

C:\python34\python ..\cx_freeze\setup.py build > freezing.log

set /p VERSION=<..\..\thonny\VERSION
"C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=%VERSION% inno_setup.iss > installer_building.log
pause