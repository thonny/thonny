@echo off

set BUILDDIR=pythonny

@echo ............... INSTALLING THONNY ...................................
%BUILDDIR%\python.exe -m pip install --pre --no-cache-dir thonny

@echo ............... INSTALLING Tkinterhtml ...................................
%BUILDDIR%\python.exe -m pip install --pre --no-cache-dir tkinterhtml


@echo ............... INSTALLING easygui ...................................
%BUILDDIR%\python.exe -m pip install --no-cache-dir easygui


@echo ............... INSTALLING PYGAME ...................................
%BUILDDIR%\python.exe -m pip install --no-cache-dir c:\pygame_wheel\pygame-1.9.2a0-cp35-none-win32.whl

@echo ............... CLEANING PYGAME ...................................
rmdir %BUILDDIR%\Lib\site-packages\pygame\tests /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\pygame\examples /S /Q>NUL
rmdir %BUILDDIR%\Lib\site-packages\pygame\docs /S /Q>NUL

pause
