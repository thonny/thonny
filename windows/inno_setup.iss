#define AppVer "0.1"
; You can give PyVer and AppVer from command line, eg:
; "C:\Program Files (x86)\Inno Setup 5\iscc" /dPyVer=2.8 /dAppVer=1.13 inno_setup.iss 

[Setup]
AppId=Thonny
AppName=Thonny
AppVersion={#AppVer}
AppVerName=Thonny {#AppVer}
;AppComments string is displayed on the "Support" dialog of the Add/Remove Programs Control Panel applet
AppComments=Thonny is beginners' Python IDE
AppPublisher=Aivar Annamaa
AppPublisherURL=https://bitbucket.org/aivarannamaa/thonny
AppSupportURL=https://bitbucket.org/aivarannamaa/thonny
AppUpdatesURL=https://bitbucket.org/aivarannamaa/thonny
DefaultDirName={pf}\Thonny
DirExistsWarning=auto
UsePreviousAppDir=yes
DefaultGroupName=Thonny
DisableProgramGroupPage=yes
;DisableDirPage=yes
DisableReadyPage=yes
;DisableWelcomePage=yes
LicenseFile=..\src\license.txt
OutputDir=dist
OutputBaseFilename=Thonny-{#AppVer}
Compression=lzma
SolidCompression=yes
WizardImageFile=inno_setup.bmp
;PrivilegesRequired=lowest
ChangesAssociations=yes


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "ShortcutLauncher\Release\ShortcutLauncher.exe"; DestDir: "{app}"; DestName: "Thonny.exe"; Flags: ignoreversion
Source: "..\src\*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\src\locale\*"; DestDir: "{app}\locale"; Flags: ignoreversion recursesubdirs
Source: "..\src\res\*.gif"; DestDir: "{app}\res"; Flags: ignoreversion
;Source: "..\src\res\*.ico"; DestDir: "{app}\res"; Flags: ignoreversion
Source: "..\src\VERSION"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; TODO: AppUserModelID ? http://msdn.microsoft.com/en-us/library/windows/desktop/dd378459%28v=vs.85%29.aspx
; TODO: pinning?
Name: "{group}\Thonny";         Filename: "{app}\Thonny.exe"; IconFilename: "{app}\Thonny.exe"
Name: "{commondesktop}\Thonny"; Filename: "{app}\Thonny.exe"; IconFilename: "{app}\Thonny.exe"

; TODO: use concrete pythonw.exe in order to let shortcut affect the pinning
; When newer Python is installed, which is better a) Thonny keeps using the version fixed during its installation, or b) Thonny uses latest Python (via pyw.exe)
Name: "{app}\Thonny_shortcut";  Filename: "C:\Windows\pyw.exe"; Parameters: "-3 -B ""{app}\main.py"""; IconFilename: "{app}\Thonny.exe"; AppUserModelID: "AivarAnnamaa.Thonny"
;Name: "{app}\Thonny_shortcut";  Filename: "C:\Windows\pyw.exe"; Parameters: "-3 -B ""d:\workspaces\python_stuff\thonny\src\main.py"""; IconFilename: "{app}\Thonny.exe"; AppUserModelID: "AivarAnnamaa.Thonny"
; "-B" because when user executes Thonny, it doesn't have permission to write pyc files anyway. 
; If installer did write these, it would possibly cause problems when python version is changed

[Registry]

; Register the application
; http://msdn.microsoft.com/en-us/library/windows/desktop/ee872121%28v=vs.85%29.aspx
Root: HKLM; Subkey: "Software\Classes\Applications\Thonny.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Thonny"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\Thonny.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Thonny"; Flags: uninsdeletekey


; http://superuser.com/questions/51264/how-do-i-add-new-applications-to-the-set-default-programs-list-in-windows-vist
Root: HKLM; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "Thonny"; ValueData: "Software\Thonny\Capabilities";  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Thonny\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Thonny\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Thonny\Capabilities\FileAssociations"; ValueType: string; ValueName: ".py"; ValueData: "Thonny.py";  Flags: uninsdeletekey

; TODO: assuming entry for Python.File is made already
;Root: HKCU; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny for Python {#PyVer}"; Flags: uninsdeletekey
;Root: HKCU; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny for Python {#PyVer}\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Thonny.exe"" ""%1"""; Flags: uninsdeletekey

; Register application and supported types
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\Thonny.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\Thonny.exe"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\Thonny.exe\SupportedTypes"; ValueType: string; ValueName: ".py"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\Thonny.exe\SupportedTypes"; ValueType: string; ValueName: ".pyw"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\Thonny.exe\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Thonny.exe"" ""%1"""; Flags: uninsdeletekey

; *.py
Root: HKLM; Subkey: "Software\Classes\.py\OpenWithProgIds"; ValueType: string; ValueName: "Thonny.py";   Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\.py\OpenWithList\Thonny.exe"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Thonny.py\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Thonny.exe"" ""%1""";  Flags: uninsdeletekey

[UninstallDelete]
Type: files; Name: "{app}\*.pyc"
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
ClickNext=
WelcomeLabel1=Thonny
WelcomeLabel2=Click "Next" to install [name/ver] %n%n-.-- . .- .... --..--   .- ... -.-. .. ..   .- .-. -   .-- --- ..- .-.. -..   .... .- ...- .   -... . . -.   -... . - - . .-. --..--   -... ..- -   .-- .. - ....   ...- .- .-. .. .- -... .-.. . -....- .-- .. -.. - ....   ..-. --- -. -   .. - .----. ...   -. ---   --. --- --- -.. .-.-.-  %n%n..-. .. .-. ... -   ..   .-- .- ...   -- . ... ... .. -. --.   .-- .. - ....   -.. .. ... - ..- - .. .-.. ...   .. -. ... - .- .-.. .-.. . .-. --..--   -... ..- -   .-.. --- --- -.- ...   .-.. .. -.- .   .-- .. -. .. -. ... -   .. -. ... - .- .-.. .-.. . .-.   -.. --- . ... -. .----. -   .-. ..- -.   - .... .   .--. --- ... -   .. -. ... - .- .-.. .-.. .- - .. --- -.   ... -.-. .-. .. .--. -   .-- .... . -.   ..- -. .. -. ... - .- .-.. .-.. .. -. --.   - .... .   .- .--. .--. .-.-.-   ... ---   ..   .-- . -. -   ..-. --- .-.   .. -. -. ---   ... . - ..- .--.   .- -. -..   .. .----. --   .-. . .- .-.. .-.. -.--   .... .- .--. .--. -.--   .-- .. - ....   .. - .-.-.-   - .... .- -. -.-   -.-- --- ..- --..--   .--- --- .-. -.. .- -.   .-. ..- ... ... . .-.. .-.. 
FinishedHeadingLabel=Great success!
FinishedLabel=[name] is now installed!%n%n%n/ \ / \ / \ / / / / \ / / / \ \ / / / / \ / / \ \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / / / / / / / / / \ / \ / \ \ \ / / / \ \ \ / \ \ \ \ / \ / \ \ / / \ \ \ / / / \ \ \ / \ / \ / / \ / \ / \ \  

ClickFinish=


[Code]
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpLicense then
    WizardForm.NextButton.Caption := SetupMessage(msgButtonInstall)
  else if CurPageID <> wpFinished then
    WizardForm.NextButton.Caption := SetupMessage(msgButtonNext);
end;

procedure InitializeWizard;
begin
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;
