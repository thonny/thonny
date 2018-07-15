; Give AppVer from command line, eg:
; "C:\Program Files (x86)\Inno Setup 5\iscc" /dAppVer=1.13 inno_setup.iss 
#define AppVer "9.9.9"
#define SourceFolder "C:\workspaces\python_stuff\thonny\packaging\windows\dummy"
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
AppPublisherURL=http://thonny.org
AppSupportURL=http://thonny.org
AppUpdatesURL=http://thonny.org

MinVersion=6.0

DisableWelcomePage=no
DisableProgramGroupPage=yes
DefaultGroupName=Thonny

AlwaysShowDirOnReadyPage=yes
; TODO: always show for admin install?
DisableDirPage=auto
DirExistsWarning=auto
UsePreviousAppDir=yes

PrivilegesRequired=lowest
OutputBaseFilename=thonny-{#AppVer}
; Note that DefaultDirName can be overridden with installer's /DIR=... parameter
DefaultDirName={code:ProposedDir}

DisableReadyPage=no
LicenseFile=license-for-win-installer.txt
OutputDir=dist
Compression=lzma2/ultra
SolidCompression=yes
WizardImageFile=screenshot_with_logo.bmp
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
;SignTool=signtool /d $qInstaller for Thonny {#AppVer}$q /du $qhttp://thonny.org$q $f


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[InstallDelete]
; TODO: dangerous, when user specified a bad directory
Type: filesandordirs; Name: "{app}\*"

; Delete old shortcut
Type: filesandordirs; Name: "{userstartmenu}\Thonny"
Type: filesandordirs; Name: "{userstartmenu}\Thonny.lnk"


; LEFTOVERS FROM OBSOLETE VERSIONS
; Delete old format settings. New filename is configuration.ini
Type: filesandordirs; Name: "{%USERPROFILE}\.thonny\preferences.ini"
; Delete backend directory (Thonny occasionally fails to delete it at runtime)
Type: filesandordirs; Name: "{%USERPROFILE}\.thonny\backend"
; Delete old 3rd party libs
Type: filesandordirs; Name: "{%USERPROFILE}\.thonny\Python35"
; TEMP
;Type: filesandordirs; Name: "{%USERPROFILE}\.thonny\BundledPython36"
Type: filesandordirs; Name: "{%USERPROFILE}\.thonny\Py36"

[Files]
Source: "{#SourceFolder}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{userprograms}\Thonny"; Filename: "{app}\thonny.exe"; IconFilename: "{app}\thonny.exe"
Name: "{userdesktop}\Thonny"; Filename: "{app}\thonny.exe"; IconFilename: "{app}\thonny.exe"


[Registry]
;Python.File

; Register the application
; http://msdn.microsoft.com/en-us/library/windows/desktop/ee872121%28v=vs.85%29.aspx
; https://docs.microsoft.com/en-us/windows/desktop/shell/app-registration
; TODO: investigate also SupportedProtocols subkey of this key
Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\thonny.exe"; ValueType: string; ValueName: "";                 ValueData: "{app}\thonny.exe"; Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\thonny.exe"; ValueType: string; ValueName: "";                 ValueData: "{app}\thonny.exe"; Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "";                 ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "";                 ValueData: "Thonny";  Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "FriendlyAppName";  ValueData: "Thonny";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "FriendlyAppName";  ValueData: "Thonny";  Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "AppUserModelID";   ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe";                       ValueType: string; ValueName: "AppUserModelID";   ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".py";              ValueData: "";        Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".py";              ValueData: "";        Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".pyw";             ValueData: "";        Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe\SupportedTypes";        ValueType: string; ValueName: ".pyw";             ValueData: "";        Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe\shell\open\command";    ValueType: string; ValueName: "";                 ValueData: """{app}\thonny.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe\shell\open\command";    ValueType: string; ValueName: "";                 ValueData: """{app}\thonny.exe"" ""%1"""; Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Applications\thonny.exe\shell\Edit with Thonny\command";   ValueType: string; ValueName: "";      ValueData: """{app}\thonny.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Applications\thonny.exe\shell\Edit with Thonny\command";   ValueType: string; ValueName: "";      ValueData: """{app}\thonny.exe"" ""%1"""; Flags: uninsdeletekey

; Add link to Thonny under existing Python.File ProgID
Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny"; ValueType: none; Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny"; ValueType: none; Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny\command"; ValueType: string; ValueName: ""; ValueData: """{app}\thonny.exe"" ""%1""";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\Python.File\shell\Edit with Thonny\command"; ValueType: string; ValueName: ""; ValueData: """{app}\thonny.exe"" ""%1""";  Flags: uninsdeletekey

; Create separate ProgID (Thonny.py) which represents Thonny's ability to handle Python files
; These settings will be used when user chooses Thonny as default program for opening *.py files
Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "";                 ValueData: "Python file";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "";                 ValueData: "Python file";  Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Python file";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Python file";  Flags: uninsdeletekey

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "AppUserModelID"; ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "AppUserModelID"; ValueData: "{#AppUserModelID}";  Flags: uninsdeletekey

;Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "EditFlags"; TODO: https://docs.microsoft.com/en-us/windows/desktop/api/Shlwapi/ne-shlwapi-filetypeattributeflags
;Root: HKCU; Check: StartedForAllUsers; Subkey: "Software\Classes\{#ThonnyPyProgID}"; ValueType: string; ValueName: "EditFlags"; TODO: https://docs.microsoft.com/en-us/windows/desktop/api/Shlwapi/ne-shlwapi-filetypeattributeflags

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\{#ThonnyPyProgID}\shell\open\command";     ValueType: string; ValueName: ""; ValueData: """{app}\thonny.exe"" ""%1""";  Flags: uninsdeletekey
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\{#ThonnyPyProgID}\shell\open\command";     ValueType: string; ValueName: ""; ValueData: """{app}\thonny.exe"" ""%1""";  Flags: uninsdeletekey

; Relate this ProgID with *.py and *.pyw extensions
; https://docs.microsoft.com/en-us/windows/desktop/shell/how-to-include-an-application-on-the-open-with-dialog-box
Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\.py\OpenWithProgIds";  ValueType: string; ValueName: "{#ThonnyPyProgID}";   Flags: uninsdeletevalue
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\.py\OpenWithProgIds";  ValueType: string; ValueName: "{#ThonnyPyProgID}";   Flags: uninsdeletevalue

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\.pyw\OpenWithProgIds"; ValueType: string; ValueName: "{#ThonnyPyProgID}";   Flags: uninsdeletevalue
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\.pyw\OpenWithProgIds"; ValueType: string; ValueName: "{#ThonnyPyProgID}";   Flags: uninsdeletevalue

; Add "Python file" to Explorer's "New" context menu (don't remove on uninstallation)
Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\.py\ShellNew";  ValueType: string; ValueData: "Python.File";  
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\.py\ShellNew";  ValueType: string; ValueData: "Python.File";  

Root: HKCU; Check: StartedForThisUser; Subkey: "Software\Classes\.py\ShellNew";  ValueType: string; ValueName: "NullFile"; ValueData: "";  
Root: HKLM; Check: StartedForAllUsers; Subkey: "Software\Classes\.py\ShellNew";  ValueType: string; ValueName: "NullFile"; ValueData: "";  

; Cleaning up old stuff
; Was: Restore "Edit with IDLE" when selecting Thonny as default opener
Root: HKCU; Subkey: "Software\Classes\{#ThonnyPyProgID}\shell\Edit with IDLE"; ValueType: none; Flags: deletekey dontcreatekey uninsdeletekey

[Run]
Filename: "{app}\pythonw.exe"; Parameters: "-m compileall ."; StatusMsg: "Compiling standard library..."


[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"
Type: filesandordirs; Name: "{app}"

[Messages]
FinishedHeadingLabel=Great success!
FinishedLabel=[name] is now installed. Run it via shortcut or right-click a *.py file and select "Edit with Thonny".%n%n%n/ \ / \ / \ / / / / \ / / / \ \ / / / / \ / / \ \ / / / / / \ \ \ \ \ \ / \ / / / / \ \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / / / / / / / / / \ / \ / \ \ \ / / / \ \ \ / \ \ \ \ / \ / \ \ / / \ \ \ / / / \ \ \ / \ / \ / / \ / \ / \ \ / \ \ / / / / / \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / / / / \ \ \ \ \ \ / \ / / \ / \ \ \ \ / / \ / \ / \ / / / / / \ \ \ \ / / \ / / / / \ / \ \ \ / / \ / / \ / / \ / / \ / / / \ \ \ \ \ \ / / \ \ / \ / / \ / / / \ / / / \ / / / / \ / / \ / / / \ \ \ \ / \ \ / \ \ \ / \ \ \ / \ \ / / \ / \ \ \ / \ / / \ / \ \ / \ / \ \ / \ / / \ \ / / / \ \ \ / \ / / \ / / / / \ \ \ / / \ / / \ / / / / \ / / / / / \ \ \ / \ / \ / \ / / \ / / \ / 

ClickFinish=


[Code]

function StartedForAllUsers(): Boolean;
begin
    Result := IsAdminLoggedOn();
end;

function StartedForThisUser(): Boolean;
begin
    Result := not IsAdminLoggedOn();
end;

function InstalledForAllUsers(): Boolean;
begin
    Result := RegKeyExists(HKEY_LOCAL_MACHINE, 'Software\Classes\Applications\thonny.exe');
end;

function InstalledForThisUser(): Boolean;
begin
    Result := RegKeyExists(HKEY_CURRENT_USER, 'Software\Classes\Applications\thonny.exe');
end;


function ProposedDir(Param: String): String;
begin
    if ExpandConstant('{param:DIR|-}') <> '-' then
      Result := ExpandConstant('{param:DIR}')
    else if StartedForAllUsers() then
      Result := ExpandConstant('{pf}\Thonny')
    else
      Result := ExpandConstant('{userpf}\Thonny');
end;

procedure InitializeWizard;
var
MoreInfoLabel: TLabel;
DualWarningLabel: TLabel;
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to using Thonny!';

  MoreInfoLabel := TLabel.Create(WizardForm);
  DualWarningLabel := TLabel.Create(WizardForm);

  if StartedForAllUsers() then
  begin
    WizardForm.WelcomeLabel2.Caption := 'This wizard will install Thonny {#AppVer} for all users.';
    MoreInfoLabel.Caption := '';
    if InstalledForThisUser() then
    begin    
      DualWarningLabel.Caption := 'Warning!'
          + ''#13#10''
          + ''#13#10''
          + 'Looks like you have already installed Thonny for your account. In order to avoid confusion, it is recommended you cancel this wizard and uninstall single-user Thonny first.';
    end
    else if InstalledForAllUsers() then
    begin
      WizardForm.WelcomeLabel2.Caption := 'This wizard will upgrade Thonny to version {#AppVer}.'
    end;
  end
  else
  begin
    WizardForm.WelcomeLabel2.Caption := 'This wizard will install Thonny {#AppVer} for your account.';
    if InstalledForAllUsers() then
    begin    
      DualWarningLabel.Caption := 'Warning!'
        + ''#13#10''
        + ''#13#10''
        + 'Looks like Thonny is already installed for all users. In order to avoid confusion, it is recommended you cancel this wizard and uninstall all-users Thonny first.';
    end
    else if InstalledForThisUser() then
    begin
      WizardForm.WelcomeLabel2.Caption := 'This wizard will upgrade Thonny to version {#AppVer}.'
      MoreInfoLabel.Caption := 'If you want to install Thonny for all users, cancel the installer, uninstall Thonny from your account and run the installer again as administrator '
          + '(right-click the installer executable and select "Run as administrator").';
    end
    else
    begin
      MoreInfoLabel.Caption := 'If you want to install Thonny for all users, cancel the installer and run it as administrator '
          + '(right-click the installer executable and select "Run as administrator").';
    end;

  end;

  WizardForm.WelcomeLabel2.AutoSize := True;

  MoreInfoLabel.Parent := WizardForm.WelcomePage;
  MoreInfoLabel.AutoSize := True;
  MoreInfoLabel.WordWrap := True;
  MoreInfoLabel.Left := WizardForm.WelcomeLabel2.Left;
  MoreInfoLabel.Width := WizardForm.WelcomeLabel2.Width;
  MoreInfoLabel.Font.Style := [fsItalic];
  MoreInfoLabel.Top := WizardForm.WelcomeLabel2.Top + WizardForm.WelcomeLabel2.Height + ScaleY(20);

  DualWarningLabel.Parent := WizardForm.WelcomePage;
  DualWarningLabel.AutoSize := True;
  DualWarningLabel.WordWrap := True;
  DualWarningLabel.Left := WizardForm.WelcomeLabel2.Left;
  DualWarningLabel.Width := WizardForm.WelcomeLabel2.Width;
  DualWarningLabel.Font.Style := [fsBold];
  //DualWarningLabel.Color := clRed;
  DualWarningLabel.Top := WizardForm.WelcomePage.Height - DualWarningLabel.Height - ScaleY(20);

  
  // make accepting license the default
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;

