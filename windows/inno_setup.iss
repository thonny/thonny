; Give AppVer from command line, eg:
; "C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=1.13 inno_setup.iss 
; #define AppVer "0.0.0"

#define AppUserModelID "Thonny.Thonny"
#define ThonnyPyProgID "Thonny.py"


[Setup]
AppId=Thonny
AppName=Thonny
AppVersion={#AppVer}
AppVerName=Thonny {#AppVer}
;AppComments string is displayed on the "Support" dialog of the Add/Remove Programs Control Panel applet
AppComments=Thonny is Python IDE for beginners
AppPublisher=Aivar Annamaa
AppPublisherURL=https://bitbucket.org/aivarannamaa/thonny
AppSupportURL=https://bitbucket.org/aivarannamaa/thonny
AppUpdatesURL=https://bitbucket.org/aivarannamaa/thonny
DefaultDirName={userpf}\Thonny
DirExistsWarning=auto
UsePreviousAppDir=yes
DefaultGroupName=Thonny
DisableProgramGroupPage=yes
DisableReadyPage=yes
LicenseFile=..\src\license.txt
OutputDir=dist
OutputBaseFilename=Thonny-{#AppVer}
Compression=lzma
SolidCompression=yes
WizardImageFile=inno_setup.bmp
PrivilegesRequired=lowest
ChangesAssociations=yes

; Signing
; Certum Unizeto provides free certs for open source
; http://www.certum.eu/certum/cert,offer_en_open_source_cs.xml
; http://pete.akeo.ie/2011/11/free-code-signing-certificate-for-open.html
; http://blog.ksoftware.net/2011/07/exporting-your-code-signing-certificate-to-a-pfx-file-from-firefox/
; http://blog.ksoftware.net/2011/07/how-to-automate-code-signing-with-innosetup-and-ksign/
SignTool=signtool /d $qInstaller for Thonny {#AppVer}$q /du $qhttps://bitbucket.org/aivarannamaa/thonny$q $f


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
Name: "{app}\Thonny";  Filename: "{code:GetPythonCommand}"; Parameters: """{app}\main.py"""; IconFilename: "{app}\Thonny.exe"; AppUserModelID: "{#AppUserModelID}"

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

; Create separate ProgID (Thonny.py) which represents Thonny's ability to handle Python files
; These settings will be used when user chooses Thonny as default program for opening *.py files
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "";                 ValueData: "Python file";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Python file";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "AppUserModelID"; ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}\shell\open\command";     ValueType: string; ValueName: ""; ValueData: """{app}\Thonny.exe"" ""%1""";  Flags: uninsdeletekey

; Restore "Edit with IDLE" when selecting Thonny as default opener
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}\shell\Edit with IDLE\command";     ValueType: string; ValueName: ""; ValueData: "C:\Windows\pyw.exe -3 -m idlelib ""%1""";  Flags: uninsdeletekey


; Relate this ProgID with *.py and *.pyw extensions
Root: HKCU; Subkey: "Software\Classes\.py\OpenWithProgIds";  ValueType: string; ValueName: "{#ThonnyPyProgID}";   Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.pyw\OpenWithProgIds"; ValueType: string; ValueName: "{#ThonnyPyProgID}";   Flags: uninsdeletevalue

; Add "Python file" to Explorer's "New" context menu
Root: HKCU; Subkey: "Software\Classes\.py\ShellNew";  ValueType: string; ValueData: "Python.File";  
Root: HKCU; Subkey: "Software\Classes\.py\ShellNew";  ValueType: string; ValueName: "NullFile"; ValueData: "";  


; Register Thonny under Default Programs
; http://superuser.com/questions/51264/how-do-i-add-new-applications-to-the-set-default-programs-list-in-windows-vist
; http://msdn.microsoft.com/en-us/library/windows/desktop/cc144154%28v=vs.85%29.aspx
; Unfortunately HKLM can't be written without elevating permissions. I chose user-install over Default Programs
; Root: HKLM; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "Thonny"; ValueData: "Software\Thonny\Capabilities"; Flags: uninsdeletevalue
; Root: HKLM; Subkey: "Software\Thonny\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "Thonny";  Flags: uninsdeletekey
; Root: HKLM; Subkey: "Software\Thonny\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Thonny is Python IDE for beginners";  Flags: uninsdeletekey
; Root: HKLM; Subkey: "Software\Thonny\Capabilities\FileAssociations"; ValueType: string; ValueName: ".py";  ValueData: "Thonny.py";  Flags: uninsdeletekey
; Root: HKLM; Subkey: "Software\Thonny\Capabilities\FileAssociations"; ValueType: string; ValueName: ".pyw"; ValueData: "Thonny.py";  Flags: uninsdeletekey


[UninstallDelete]
Type: files; Name: "{app}\*.pyc"
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
ClickNext=
WelcomeLabel1=Install Thonny {#AppVer} ?
WelcomeLabel2=Click "Next" if that's what you want! %n%n-.-- . .- .... --..--   .- ... -.-. .. ..   .- .-. -   .-- --- ..- .-.. -..   .... .- ...- .   -... . . -.   -... . - - . .-. --..--   -... ..- -   .-- .. - ....   ...- .- .-. .. .- -... .-.. . -....- .-- .. -.. - ....   ..-. --- -. -   .. - .----. ...   -. ---   --. --- --- -.. .-.-.-  %n%n..-. .. .-. ... -   ..   .-- .- ...   -- . ... ... .. -. --.   .-- .. - ....   -.. .. ... - ..- - .. .-.. ...   .. -. ... - .- .-.. .-.. . .-. --..--   -... ..- -   .-.. --- --- -.- ...   .-.. .. -.- .   .-- .. -. .. -. ... -   .. -. ... - .- .-.. .-.. . .-.   -.. --- . ... -. .----. -   .-. ..- -.   - .... .   .--. --- ... -   .. -. ... - .- .-.. .-.. .- - .. --- -.   ... -.-. .-. .. .--. -   .-- .... . -.   ..- -. .. -. ... - .- .-.. .-.. .. -. --.   - .... .   .- .--. .--. .-.-.-   ... ---   ..   .-- . -. -   ..-. --- .-.   .. -. -. ---   ... . - ..- .--.   .- -. -..   .. .----. --   .-. . .- .-.. .-.. -.--   .... .- .--. .--. -.--   .-- .. - ....   .. - .-.-.-   - .... .- -. -.-   -.-- --- ..- --..--   .--- --- .-. -.. .- -.   .-. ..- ... ... . .-.. .-.. 
FinishedHeadingLabel=Great success!
FinishedLabel=[name] is now installed. Run it via shortcut or right-click a *.py file and select "Edit with Thonny".%n%n%n/ \ / \ / \ / / / / \ / / / \ \ / / / / \ / / \ \ / / / / / \ \ \ \ \ \ / \ / / / / \ \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / / / / / / / / / \ / \ / \ \ \ / / / \ \ \ / \ \ \ \ / \ / \ \ / / \ \ \ / / / \ \ \ / \ / \ / / \ / \ / \ \ / \ \ / / / / / \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / \ / 

ClickFinish=


[Code]

function TryRegQueryStringValue(const RootKey: Integer; const SubKeyName, ValueName: String; var ResultStr: String): Boolean;
begin
  try
    Result := RegQueryStringValue(RootKey, SubKeyName, ValueName, ResultStr);
  except
    Result := False;
  end;
end;



function GetPythonFolder(version: string): string;
var          
  reg1 : string;
  reg2 : string;
begin
  reg1 := 'SOFTWARE\Python\PythonCore\' + version + '\InstallPath';
  reg2 := 'SOFTWARE\Python\PythonCore\Wow6432Node\' + version + '\InstallPath';

  if not (TryRegQueryStringValue(HKLM64, reg1, '', Result) 
       or TryRegQueryStringValue(HKCU64, reg1, '', Result)
       or TryRegQueryStringValue(HKLM32, reg1, '', Result)
       or TryRegQueryStringValue(HKCU32, reg1, '', Result)
       or TryRegQueryStringValue(HKLM, reg2, '', Result)) then
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
    Result := 'C:\Python34\pythonw.exe' // my best guess
    MsgBox('Could not find information about suitable Python version (3.3 or 3.4). Update the shortcut in Thonny folder after installation ends.',mbError,MB_OK);
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

function Version(Param: String): String;
var
  VersionValue: AnsiString;
  VersionFile: String;
begin
  // Default to some predefined value.
  Result := '0.0.0';
  VersionFile := '{app}\VERSION';
  if LoadStringFromFile(VersionFile, VersionValue) then
    Result := Trim(VersionValue);
end;
