@echo off

set PREFIX=pythonny
set BUILDDIR=build
rmdir %BUILDDIR% /S /Q
mkdir %BUILDDIR%

@echo ............... COPYING PYTHON ...................................
xcopy %PREFIX%\* %BUILDDIR% /S /E /K>NUL


@echo ............... INSTALLING THONNY ...................................
%BUILDDIR%\python.exe -m pip install --upgrade thonny

@echo ............... CLEANING PYTHON ...................................
rmdir %BUILDDIR%\Lib\ensurepip /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\pip /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\pip-7.1.2.dist-info /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\virtualenv_support /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\virtualenv-13.1.2.dist-info /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\setuptools /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\setuptools-18.2.dist-info /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\requests /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\requests_toolbelt /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\requests_toolbelt-0.4.0.dist-info /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\requests-2.8.1.dist-info /S /Q>NUL


@echo ............... COPYING THONNY LAUNCHER ..........................
copy ThonnyRunner\Release\thonny.exe %BUILDDIR% /Y


@echo ............... CREATING INSTALLER ..........................
set /p VERSION=<..\..\thonny\VERSION
"C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=%VERSION% /dSourceFolder=build inno_setup.iss > installer_building.log


pause
