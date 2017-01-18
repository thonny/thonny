set PREFIX=pythonny

@echo ............... CLEANING ............................
rmdir %PREFIX% /S /Q
mkdir %PREFIX%

@echo ............... COPYING PYTHON and Thonny launcher .........
xcopy .\Python35\* %PREFIX% /S /E /K>NUL
copy ThonnyRunner35\Release\thonny.exe %PREFIX% /Y

@echo ............... COPYING VS FILES ..........................
xcopy ucrt_redist\*.dll %PREFIX% /S /E /K>NUL
xcopy ucrt_redist\api-ms-win*.dll %PREFIX%\DLLs /S /E /K>NUL


pause
