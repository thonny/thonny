@SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\8.1\bin\x86

mt.exe -inputresource:%1;#1 -out:extracted.manifest
mt.exe -manifest EnableDPIAwareness.manifest extracted.manifest -out:merged.manifest
mt.exe -outputresource:%1;#1 -manifest merged.manifest

del extracted.manifest
del merged.manifest