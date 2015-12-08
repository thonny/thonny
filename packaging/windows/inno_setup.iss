; Give AppVer from command line, eg:
; "C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=1.13 inno_setup.iss 
; #define AppVer "0.0.0"
; #define SourceFolder "set_source_folder_from_command_line"

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
AppPublisherURL=http://thonny.cs.ut.ee
AppSupportURL=http://thonny.cs.ut.ee
AppUpdatesURL=http://thonny.cs.ut.ee
MinVersion=6.0
DefaultDirName={userpf}\Thonny
DirExistsWarning=auto
UsePreviousAppDir=yes
DefaultGroupName=Thonny
DisableProgramGroupPage=yes
DisableReadyPage=yes
LicenseFile=../../LICENSE.txt
OutputDir=dist
OutputBaseFilename=thonny-{#AppVer}
Compression=lzma2/ultra
SolidCompression=yes
WizardImageFile=inno_setup.bmp
PrivilegesRequired=lowest
ChangesAssociations=yes
; Request extra space for precompiling libraries
ExtraDiskSpaceRequired=25000000

; Signing
; Certum Unizeto provides free certs for open source
; http://www.certum.eu/certum/cert,offer_en_open_source_cs.xml
; http://pete.akeo.ie/2011/11/free-code-signing-certificate-for-open.html
; http://blog.ksoftware.net/2011/07/exporting-your-code-signing-certificate-to-a-pfx-file-from-firefox/
; http://certhelp.ksoftware.net/support/solutions/articles/17157-how-do-i-export-my-code-signing-certificate-from-internet-explorer-or-chrome-
; http://blog.ksoftware.net/2011/07/how-to-automate-code-signing-with-innosetup-and-ksign/
SignTool=signtool /d $qInstaller for Thonny {#AppVer}$q /du $qhttp://thonny.cs.ut.ee$q $f


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceFolder}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[InstallDelete]
; TODO: leave plugins dir 
Type: filesandordirs; Name: "{app}\*"
; Delete old format settings. New filename is configuration.ini
Type: filesandordirs; Name: "{%USERPROFILE}\.thonny\preferences.ini"

[Icons]
Name: "{userstartmenu}\Thonny"; Filename: "{app}\thonny.exe"; IconFilename: "{app}\thonny.exe"
Name: "{userdesktop}\Thonny"; Filename: "{app}\thonny.exe"; IconFilename: "{app}\thonny.exe"


[Registry]
;Python.File

; Register the application
; http://msdn.microsoft.com/en-us/library/windows/desktop/ee872121%28v=vs.85%29.aspx
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\thonny.exe"; ValueType: string; ValueName: "";                 ValueData: "{app}\thonny.exe"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe\shell\open\command";    ValueType: string; ValueName: "";                 ValueData: """{app}\thonny.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe\shell\Edit with Thonny\command";   ValueType: string; ValueName: "";      ValueData: """{app}\thonny.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".py";              ValueData: "";        Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".pyw";             ValueData: "";        Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "";                 ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "FriendlyAppName";  ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "AppUserModelID";   ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey

; Add link to Thonny under existing Python.File ProgID
Root: HKCU; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny\command"; ValueType: string; ValueName: ""; ValueData: """{app}\thonny.exe"" ""%1""";  Flags: uninsdeletekey

; Create separate ProgID (Thonny.py) which represents Thonny's ability to handle Python files
; These settings will be used when user chooses Thonny as default program for opening *.py files
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "";                 ValueData: "Python file";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Python file";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "AppUserModelID"; ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}\shell\open\command";     ValueType: string; ValueName: ""; ValueData: """{app}\thonny.exe"" ""%1""";  Flags: uninsdeletekey

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

[Run]
Filename: "{app}\pythonw.exe"; Parameters: "-m compileall ."


[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Messages]
ClickNext=
WelcomeLabel1=Installer for Thonny {#AppVer}
WelcomeLabel2=Click "Next"! %n%n-.-- . .- .... --..--   .- ... -.-. .. ..   .- .-. -   .-- --- ..- .-.. -..   .... .- ...- .   -... . . -.   -... . - - . .-. --..--   -... ..- -   .-- .. - ....   ...- .- .-. .. .- -... .-.. . -....- .-- .. -.. - ....   ..-. --- -. -   .. - .----. ...   -. ---   --. --- --- -.. .-.-.-  %n%n..-. .. .-. ... -   ..   .-- .- ...   -- . ... ... .. -. --.   .-- .. - ....   -.. .. ... - ..- - .. .-.. ...   .. -. ... - .- .-.. .-.. . .-. --..--   -... ..- -   .-.. --- --- -.- ...   .-.. .. -.- .   .-- .. -. .. -. ... -   .. -. ... - .- .-.. .-.. . .-.   -.. --- . ... -. .----. -   .-. ..- -.   - .... .   .--. --- ... -   .. -. ... - .- .-.. .-.. .- - .. --- -.   ... -.-. .-. .. .--. -   .-- .... . -.   ..- -. .. -. ... - .- .-.. .-.. .. -. --.   - .... .   .- .--. .--. .-.-.-   ... ---   ..   .-- . -. -   ..-. --- .-.   .. -. -. ---   ... . - ..- .--.   .- -. -..   .. .----. --   .-. . .- .-.. .-.. -.--   .... .- .--. .--. -.--   .-- .. - ....   .. - .-.-.-   - .... .- -. -.-   -.-- --- ..- --..--   .--- --- .-. -.. .- -.   .-. ..- ... ... . .-.. .-.. 
FinishedHeadingLabel=Great success!
FinishedLabel=[name] is now installed. Run it via shortcut or right-click a *.py file and select "Edit with Thonny".%n%n%n/ \ / \ / \ / / / / \ / / / \ \ / / / / \ / / \ \ / / / / / \ \ \ \ \ \ / \ / / / / \ \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / / / / / / / / / \ / \ / \ \ \ / / / \ \ \ / \ \ \ \ / \ / \ \ / / \ \ \ / / / \ \ \ / \ / \ / / \ / \ / \ \ / \ \ / / / / / \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / \ / 

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

