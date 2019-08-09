@echo off

set BUILDDIR=build
del %BUILDDIR% /Q
rmdir %BUILDDIR% /S /Q
mkdir %BUILDDIR%

@echo ............... COPYING PYTHON ...................................
xcopy C:\Pythonny37\* %BUILDDIR% /S /E /K>NUL
@echo ............... COPYING OTHER STUFF ...................................
copy ThonnyRunner37\Release\thonny.exe %BUILDDIR% /Y
xcopy ucrt_redist\*.dll %BUILDDIR% /S /E /K>NUL
xcopy ucrt_redist\api-ms-win*.dll %BUILDDIR%\DLLs /S /E /K>NUL
copy thonny_python.ini %BUILDDIR%

@echo ............... INSTALLING DEPS ...................................

%BUILDDIR%\python -m pip install --no-cache-dir asttokens==1.1.*
%BUILDDIR%\python -m pip install --no-cache-dir parso==0.5.*
%BUILDDIR%\python -m pip install --no-cache-dir jedi==0.14.*
%BUILDDIR%\python -m pip install --no-cache-dir --no-binary mypy mypy==0.720
%BUILDDIR%\python -m pip install --no-cache-dir pylint==2.3.*
%BUILDDIR%\python -m pip install docutils==0.15.*
%BUILDDIR%\python -m pip install pyserial==3.4

@echo ............... INSTALLING THONNY ...................................
%BUILDDIR%\python -m pip install --pre --no-cache-dir thonny

@echo ............... CLEANING PYTHON ............................
@rem delete following 3 files to avoid confusion (user may think they're Thonny license etc.)
del %BUILDDIR%\LICENSE.txt>NUL
del %BUILDDIR%\README.txt>NUL
del %BUILDDIR%\NEWS.txt>NUL

del /S "%BUILDDIR%\*.pyc">NUL
@rem del /S "%BUILDDIR%\*.lib">NUL
del /S "%BUILDDIR%\tcl\*.lib">NUL
del /S "%BUILDDIR%\*.a">NUL
del /S "%BUILDDIR%\*.chm">NUL

rmdir %BUILDDIR%\Doc /S /Q>NUL
@rem rmdir %BUILDDIR%\include /S /Q>NUL
@rem rmdir %BUILDDIR%\libs /S /Q>NUL
rmdir %BUILDDIR%\Tools /S /Q>NUL
del "%BUILDDIR%\Scripts\*" /Q>NUL

copy .\pip.bat "%BUILDDIR%\Scripts\pip.bat"
copy .\pip.bat "%BUILDDIR%\Scripts\pip3.bat"
copy .\pip.bat "%BUILDDIR%\Scripts\pip3.7.bat"

rmdir %BUILDDIR%\lib\test /S /Q>NUL

del %BUILDDIR%\tcl\*.sh /Q>NUL
del %BUILDDIR%\tcl\tcl8.6\clock.tcl>NUL
del %BUILDDIR%\tcl\tcl8.6\safe.tcl>NUL
rmdir %BUILDDIR%\tcl\tix8.4.3\demos /S /Q>NUL

rmdir %BUILDDIR%\tcl\tk8.6\demos /S /Q>NUL
rmdir %BUILDDIR%\tcl\tk8.6\msgs /S /Q>NUL

rmdir %BUILDDIR%\tcl\tcl8.6\opt0.4 /S /Q>NUL
rmdir %BUILDDIR%\tcl\tcl8.6\msgs /S /Q>NUL
rmdir %BUILDDIR%\tcl\tcl8.6\tzdata /S /Q>NUL

rmdir %BUILDDIR%\lib\site-packages\pylint\test /S /Q>NUL
rmdir %BUILDDIR%\lib\site-packages\mypy\test /S /Q>NUL


@echo ............... ADDING LICENSES ...................................
copy ..\..\LICENSE.txt %BUILDDIR% /Y>NUL
mkdir %BUILDDIR%\licenses
xcopy ..\..\licenses\* %BUILDDIR%\licenses /S /E /K>NUL

@echo ............... ADDING OTHER STUFF ...................................
copy ..\..\CHANGELOG.rst %BUILDDIR% /Y>NUL
copy ..\..\CREDITS.rst %BUILDDIR% /Y>NUL
copy ..\..\README.rst %BUILDDIR% /Y>NUL


@echo ............... CREATING INSTALLER ..........................
set /p VERSION=<%BUILDDIR%\Lib\site-packages\thonny\VERSION
"C:\Program Files (x86)\Inno Setup 6\iscc" /dAppVer=%VERSION% /dSourceFolder=build inno_setup.iss > installer_building.log

@echo ............... CREATING ZIP ..........................
SET PATH=%PATH%;C:\Program Files\7-Zip
cd %BUILDDIR%
7z a -tzip ..\dist\thonny-%VERSION%-windows.zip *


@rem rmdir %BUILDDIR% /S /Q
pause
