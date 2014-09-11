#define AppVer "0.1"
#define AppUserModelID "Thonny.Thonny"
#define PyProgID "Thonny.py"

; You can give AppVer from command line, eg:
; "C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=1.13 inno_setup.iss 

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
DefaultDirName={userpf}\Thonny
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
PrivilegesRequired=lowest
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
Name: "{userstartmenu}\Thonny"; Filename: "{app}\Thonny.exe"; IconFilename: "{app}\Thonny.exe"
Name: "{userdesktop}\Thonny";   Filename: "{app}\Thonny.exe"; IconFilename: "{app}\Thonny.exe"

; Using concrete pythonw.exe instead of pyw.exe in order to let shortcut affect the pinning
; "-B" because when user executes Thonny, it doesn't have permission to write pyc files anyway. 
; If installer did write these, it would possibly cause problems when python version is changed
Name: "{app}\Thonny";  Filename: "{code:GetPythonCommand}"; Parameters: "-B ""{app}\main.py"""; IconFilename: "{app}\Thonny.exe"; AppUserModelID: "{#AppUserModelID}"

[Registry]
;Python.File

; Register the application
; http://msdn.microsoft.com/en-us/library/windows/desktop/ee872121%28v=vs.85%29.aspx
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\Thonny.exe"; ValueType: string; ValueName: "";                 ValueData: "{app}\Thonny.exe"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe\shell\open\command";    ValueType: string; ValueName: "";                 ValueData: """{app}\Thonny.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe\shell\Edit with Thonny\command";   ValueType: string; ValueName: "";      ValueData: """{app}\Thonny.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".py";              ValueData: "";        Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".pyw";             ValueData: "";        Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe";                       ValueType: string; ValueName: "";                 ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe";                       ValueType: string; ValueName: "FriendlyAppName";  ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\Thonny.exe";                       ValueType: string; ValueName: "AppUserModelID";   ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey

; Add link to Thonny under existing Python.File ProgID
Root: HKCU; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Thonny.exe"" ""%1""";  Flags: uninsdeletekey

; Create separate ProgID (Thonny.py) for relating Thonny and Python file type
; These settings will be used when user chooses Thonny as default program for opening *.py files
Root: HKCU; Subkey: "Software\Classes\{#PyProgID}"; ValueType: string; ValueName: "";                 ValueData: "Python file";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#PyProgID}"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Python file";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#PyProgID}"; ValueType: string; ValueName: "AppUserModelID"; ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#PyProgID}\shell\open\command";     ValueType: string; ValueName: ""; ValueData: """{app}\Thonny.exe"" ""%1""";  Flags: uninsdeletekey
; Relate this ProgID with *.py and *.pyw extensions
Root: HKCU; Subkey: "Software\Classes\.py\OpenWithProgIds";  ValueType: string; ValueName: "{#PyProgID}";   Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.pyw\OpenWithProgIds"; ValueType: string; ValueName: "{#PyProgID}";   Flags: uninsdeletekey


; Registering under Default Programs
; http://superuser.com/questions/51264/how-do-i-add-new-applications-to-the-set-default-programs-list-in-windows-vist
; http://msdn.microsoft.com/en-us/library/windows/desktop/cc144154%28v=vs.85%29.aspx
;Root: HKLM; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "Thonny"; ValueData: "Software\Thonny\Capabilities";  Flags: uninsdeletekey
;Root: HKLM; Subkey: "Software\Thonny\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Thonny";  Flags: uninsdeletekey
;Root: HKLM; Subkey: "Software\Thonny\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "Thonny";  Flags: uninsdeletekey
;Root: HKLM; Subkey: "Software\Thonny\Capabilities\FileAssociations"; ValueType: string; ValueName: ".py"; ValueData: "Thonny.py";  Flags: uninsdeletekey




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

function GetPythonFolder(version: string): string;
var          
  reg1 : string;
  reg2 : string;
begin
  reg1 := 'SOFTWARE\Python\PythonCore\' + version + '\InstallPath';
  reg2 := 'SOFTWARE\Python\PythonCore\Wow6432Node\' + version + '\InstallPath';

  if not (RegQueryStringValue(HKLM64, reg1, '', Result) 
       or RegQueryStringValue(HKCU64, reg1, '', Result)
       or RegQueryStringValue(HKLM32, reg1, '', Result)
       or RegQueryStringValue(HKCU32, reg1, '', Result)
       or RegQueryStringValue(HKLM, reg2, '', Result)
       ) then
  begin
    Result := '';
  end
end;

function GetPythonCommand(Value: string): string;
var          
  Py34 : string;
  Py33 : string;
begin
  Py34 := GetPythonFolder('3.4');
  Py33 := GetPythonFolder('3.3');

  if Py34 <> '' then
  begin
    Result := Py34 + '\pythonw.exe';
  end
  else if Py33 <> '' then
  begin
    Result := Py33 + '\pythonw.exe';
  end
  else
  begin
    MsgBox('Could not find suitable Python version (3.3 or 3.4). Update the shortcut in Thonny folder after installation ends.',mbError,MB_OK);
    Result := 'C:\PythonXX\pythonw.exe'
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
