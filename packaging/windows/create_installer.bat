@echo off

set BUILDDIR=build

@echo ............... INSTALLING THONNY ...................................
%BUILDDIR%\python.exe -m pip install --upgrade thonny

@echo ............... COPYING THONNY LAUNCHER ..........................
copy ThonnyRunner\Release\thonny.exe %BUILDDIR% /Y


@echo ............... CREATING INSTALLER ..........................
set /p VERSION=<..\..\thonny\VERSION
"C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=%VERSION% /dSourceFolder=build inno_setup.iss > installer_building.log


pause
