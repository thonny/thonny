set /p VERSION=<..\src\VERSION
"C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=%VERSION% inno_setup.iss
pause