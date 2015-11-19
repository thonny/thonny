set PREFIX=pythonny

@echo ............... CLEANING ............................
rmdir %PREFIX% /S /Q
mkdir %PREFIX%

@echo ............... COPYING PYTHON ............................
xcopy C:\Python35\* %PREFIX% /S /E /K>NUL

@echo ............... CLEANING PYTHON ............................
cd %PREFIX%
move LICENSE.txt PYTHON-LICENSE.txt>NUL
del README.txt>NUL
del NEWS.txt>NUL
del test.bat>NUL
del /S *.pyc>NUL
del /S *.lib>NUL
del /S *.a>NUL
del /S *.chm>NUL

rmdir Doc /S /Q>NUL
rmdir include /S /Q>NUL
rmdir libs /S /Q>NUL
rmdir Tools /S /Q>NUL
rmdir Scripts /S /Q>NUL

rmdir lib\test /S /Q>NUL
rmdir lib\plat-* /S /Q>NUL


del tcl\*.sh /Q>NUL
del tcl\tcl8.6\clock.tcl>NUL
del tcl\tcl8.6\safe.tcl>NUL
rmdir tcl\tix8.4.3\demos /S /Q>NUL

rmdir tcl\tk8.6\demos /S /Q>NUL
rmdir tcl\tk8.6\msgs /S /Q>NUL

rmdir tcl\tcl8.6\opt0.4 /S /Q>NUL
rmdir tcl\tcl8.6\msgs /S /Q>NUL
rmdir tcl\tcl8.6\tzdata /S /Q>NUL
cd ..

@echo ............... COPYING VS FILES ..........................
xcopy ucrt_redist\*.dll %PREFIX% /S /E /K>NUL
xcopy ucrt_redist\api-ms-win*.dll %PREFIX%\DLLs /S /E /K>NUL

@echo ............... ENABLE DPI AWARNESS ..............................
@REM call EnableDPIAwareness %PREFIX%\pythonw.exe

pause
