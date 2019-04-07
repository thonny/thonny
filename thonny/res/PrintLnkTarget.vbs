' used for getting path of network location from shortcut

set WshShell = WScript.CreateObject("WScript.Shell")
set Lnk = WshShell.Createshortcut(WScript.Arguments(0))
WScript.Echo Lnk.TargetPath

' usage cscript /Nologo PrintTarget.vbs .\shortcutname\target.lnk
