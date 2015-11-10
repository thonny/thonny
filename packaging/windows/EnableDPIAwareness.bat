@echo off

@SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\8.1\bin\x86;D:\PF\Windows Kits\10\bin\x86

mt.exe -inputresource:%1;#1 -out:extracted.manifest > nul
mt.exe -manifest EnableDPIAwareness.manifest extracted.manifest -out:merged.manifest > nul
mt.exe -outputresource:%1;#1 -manifest merged.manifest > nul

del extracted.manifest
del merged.manifest