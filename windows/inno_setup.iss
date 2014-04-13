; http://stackoverflow.com/questions/16157700/python-distribute-module-using-inno-setup
#define PyVer "2.7"
#define AppVer "0.1"
#define AppId "ThonnyPy27"
; You can give PyVer and AppVer from command line, eg:
; "C:\Program Files (x86)\Inno Setup 5\iscc" /dPyVer=2.8 /dAppVer=1.13 inno_setup.iss 

[Setup]
AppId={#AppId}
AppName=Thonny for Python {#PyVer}
AppVersion={#AppVer}
AppVerName=Thonny {#AppVer} for Python {#PyVer}
AppComments=This string is displayed on the "Support" dialog of the Add/Remove Programs Control Panel applet
AppPublisher=Aivar
AppPublisherURL=http://thonny.org/
AppSupportURL=http://thonny.org/
AppUpdatesURL=http://thonny.org/
DefaultDirName={userpf}\{#AppId}
DirExistsWarning=auto
UsePreviousAppDir=yes
DefaultGroupName=Thonny
DisableProgramGroupPage=yes
;DisableDirPage=yes
DisableReadyPage=yes
;DisableWelcomePage=yes
LicenseFile=..\src\license.txt
OutputDir=dist
OutputBaseFilename=ThonnyForPy{#PyVer}-v{#AppVer}
Compression=lzma
SolidCompression=yes
WizardImageFile=inno_setup.bmp
;PrivilegesRequired=lowest
ChangesAssociations=yes


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
source: "ShortcutLauncher\Release\ShortcutLauncher.exe"; DestDir: "{app}"; DestName: "{#AppId}.exe"; Flags: ignoreversion
Source: "..\src\*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\src\res\*.gif"; DestDir: "{app}\res"; Flags: ignoreversion
Source: "..\src\res\*.ico"; DestDir: "{app}\res"; Flags: ignoreversion
Source: "..\src\VERSION"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; TODO: AppUserModelID ? http://msdn.microsoft.com/en-us/library/windows/desktop/dd378459%28v=vs.85%29.aspx
; TODO: pinning?
Name: "{group}\Thonny for Python {#PyVer}";         Filename: "{app}\{#AppId}.exe"; IconFilename: "{app}\thonny.ico"
Name: "{commondesktop}\Thonny for Python {#PyVer}"; Filename: "{app}\{#AppId}.exe"; IconFilename: "{app}\thonny.ico"
Name: "{app}\{#AppId}_shortcut";     Filename: "{code:GetPythonPrefix}\pythonw.exe"; Parameters: "{app}\main.py"; IconFilename: "{app}\thonny.ico"

[Registry]

; pyex: protocol
; http://msdn.microsoft.com/en-us/library/aa767914%28v=vs.85%29.aspx
;Root: HKCU; Subkey: "Software\Classes\pyex"; ValueType: string; ValueName: ""; ValueData: "URL:Python exercise protocol";  Flags: uninsdeletekey
;Root: HKCU; Subkey: "Software\Classes\pyex"; ValueType: string; ValueName: "URL Protocol"; ValueData: "";  Flags: uninsdeletekey
;Root: HKCU; Subkey: "Software\Classes\pyex\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppId}.exe"" ""%1""";  Flags: uninsdeletekey


; Register the application
; http://superuser.com/questions/51264/how-do-i-add-new-applications-to-the-set-default-programs-list-in-windows-vist
Root: HKLM; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "{#AppId}"; ValueData: "Software\{#AppId}\Capabilities";  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppId}\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Thonny 27 desc";  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppId}\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "Thonny 27 name";  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppId}\Capabilities\FileAssociations"; ValueType: string; ValueName: ".py"; ValueData: "{#AppId}.py";  Flags: uninsdeletekey

; TODO: assuming entry for Python.File is made already
;Root: HKCU; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny for Python {#PyVer}"; Flags: uninsdeletekey
;Root: HKCU; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny for Python {#PyVer}\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppId}.exe"" ""%1"""; Flags: uninsdeletekey

; Register application and supported types
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#AppId}.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppId}.exe"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\{#AppId}.exe\SupportedTypes"; ValueType: string; ValueName: ".py"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\{#AppId}.exe\SupportedTypes"; ValueType: string; ValueName: ".pyw"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\{#AppId}.exe\SupportedTypes"; ValueType: string; ValueName: ".pytemplate"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Applications\{#AppId}.exe\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppId}.exe"" ""%1"""; Flags: uninsdeletekey

; *.py
Root: HKLM; Subkey: "Software\Classes\.py\OpenWithProgIds"; ValueType: string; ValueName: "{#AppId}.py";   Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\.py\OpenWithList\{#AppId}.exe"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\{#AppId}.py\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppId}.exe"" ""%1""";  Flags: uninsdeletekey

; *.pytemplate
Root: HKLM; Subkey: "Software\Classes\{#AppId}.pytemplate\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppId}.exe"" ""%1"""; Flags: uninsdeletekey
;Root: HKLM; Subkey: "Software\Classes\{#AppId}.pytemplate\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppId}.exe,-2"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\.pytemplate\OpenWithProgIds"; ValueType: string; ValueName: "{#AppId}.pytemplate";   Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\.pytemplate\OpenWithList\{#AppId}.exe"; Flags: uninsdeletekey


; http://msdn.microsoft.com/en-us/library/windows/desktop/ee872121%28v=vs.85%29.aspx#appPaths
; HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\calibre.exe
;    (Default) REG_SZ   C:\Program Files (x86)\Calibre2\calibre.exe
;    Path      REG_SZ   C:\Program Files (x86)\Calibre2\    // prepended to process'es path, not required

; HKEY_CLASSES_ROOT\Applications\ApplicationName.exe 
;     DefaultIcon
;     SupportedTypes

[UninstallDelete]
Type: files; Name: "{app}\*.pyc"
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
ClickNext=
WelcomeLabel1=Thonny for Python {#PyVer}
WelcomeLabel2=Click "Next" to install [name/ver] %n%n-.-- . .- .... --..--   .- ... -.-. .. ..   .- .-. -   .-- --- ..- .-.. -..   .... .- ...- .   -... . . -.   -... . - - . .-. --..--   -... ..- -   .-- .. - ....   ...- .- .-. .. .- -... .-.. . -....- .-- .. -.. - ....   ..-. --- -. -   .. - .----. ...   -. ---   --. --- --- -.. .-.-.-  %n%n..-. .. .-. ... -   ..   .-- .- ...   -- . ... ... .. -. --.   .-- .. - ....   -.. .. ... - ..- - .. .-.. ...   .. -. ... - .- .-.. .-.. . .-. --..--   -... ..- -   .-.. --- --- -.- ...   .-.. .. -.- .   .-- .. -. .. -. ... -   .. -. ... - .- .-.. .-.. . .-.   -.. --- . ... -. .----. -   .-. ..- -.   - .... .   .--. --- ... -   .. -. ... - .- .-.. .-.. .- - .. --- -.   ... -.-. .-. .. .--. -   .-- .... . -.   ..- -. .. -. ... - .- .-.. .-.. .. -. --.   - .... .   .- .--. .--. .-.-.-   ... ---   ..   .-- . -. -   ..-. --- .-.   .. -. -. ---   ... . - ..- .--.   .- -. -..   .. .----. --   .-. . .- .-.. .-.. -.--   .... .- .--. .--. -.--   .-- .. - ....   .. - .-.-.-   - .... .- -. -.-   -.-- --- ..- --..--   .--- --- .-. -.. .- -.   .-. ..- ... ... . .-.. .-.. 
FinishedHeadingLabel=Great success!
FinishedLabel=[name] is now installed. It lives in Python's Lib/site-packages folder. %n%nYou can launch it via shortcuts on Desktop or in Start menu, or by right-clicking a *.py file and selecting "Edit with Thonny".%n%nIf you have python in PATH, you can also do: %npython -m thonny%n%n%n/ \ / \ / \ / / / / \ / / / \ \ / / / / \ / / \ \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / / / / / / / / / \ / \ / \ \ \ / / / \ \ \ / \ \ \ \ / \ / \ \ / / \ \ \ / / / \ \ \ / \ / \ / / \ / \ / \ \  

ClickFinish=


[Code]
// http://stackoverflow.com/questions/16157700/python-distribute-module-using-inno-setup
procedure ExitProcess(exitCode:integer);
  external 'ExitProcess@kernel32.dll stdcall';

function GetPythonPrefix(Value: string): string;
var          
  reg1 : string;
  reg2 : string;
begin
  reg1 := 'SOFTWARE\Python\PythonCore\' + '{#PyVer}' + '\InstallPath';
  reg2 := 'SOFTWARE\Python\PythonCore\Wow6432Node\' + '{#PyVer}' + '\InstallPath';

  if not (RegQueryStringValue(HKLM, reg1, '', Result) 
       or RegQueryStringValue(HKCU, reg1, '', Result)
       or RegQueryStringValue(HKLM, reg2, '', Result)) then
  begin
    MsgBox('Could not find Python {#PyVer}',mbError,MB_OK);
    // TODO: then allow user to select ?
    ExitProcess(1);
  end
end;

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
