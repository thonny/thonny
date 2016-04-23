
Shortcut [Version 1.11]

Creates, modifies or queries Windows shell links (shortcuts)


The syntax of this command is:

Shortcut.exe /F:filename /A:C|E|Q [/T:target] [/P:parameters] [/W:workingdir]
         [/R:runstyle] [/I:icon,index] [/H:hotkey] [/D:description]

 /F:filename    : Specifies the .LNK shortcut file.
 /A:action      : Defines the action to take (C=Create, E=Edit or Q=Query).
 /T:target      : Defines the target path and file name the shortcut points to.
 /P:parameters  : Defines the command-line parameters to pass to the target.
 /W:working dir : Defines the working directory the target starts with.
 /R:run style   : Defines the window state (1=Normal, 3=Max, 7=Min).
 /I:icon,index  : Defines the icon and optional index (file.exe or file.exe,0).
 /H:hotkey      : Defines the hotkey, a numeric value of the keyboard shortcut.
 /D:description : Defines the description (or comment) for the shortcut.

 Notes:
 - Any argument that contains spaces must be enclosed in "double quotes".
 - If Query is specified (/A:Q), all arguments except /F: are ignored.
 - To find the numeric hotkey value, use Explorer to set a hotkey and then /A:Q
 - To prevent an environment variable from being expanded until the shortcut
   is launched, use the ^ carat escape character like this: ^%WINDIR^%

 Examples:
   /f:"%ALLUSERSPROFILE%\Start Menu\Programs\My App.lnk" /a:q
   /f:"%USERPROFILE%\Desktop\Notepad.lnk" /a:c /t:^%WINDIR^%\Notepad.exe /h:846
   /f:"%USERPROFILE%\Desktop\Notepad.lnk" /a:e /p:C:\Setup.log /r:3

 An argument of /? or -? displays this syntax and returns 1.
 A successful completion will return 0.


 Copyright 2000-2005 Marty List, www.OptimumX.com


==================================================================


Revision History:

1.11 	07/04/2005
- Fixed display problem for hotkeys with extended characters.
- Removed reference to .URL files in the syntax, since URL files are not supported yet.

1.10 	12/20/2003
- Fixed COM memory leak, enhanced exit/result codes, enhanced syntax.

1.00 	10/02/2000
- Initial release.

